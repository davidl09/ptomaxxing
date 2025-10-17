"""Generate candidate PTO windows given a labeled calendar."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable, Iterator, Sequence

from .models import CandidateWindow, DayInfo, DayType

WINDOW_RADIUS = 7
DOUBLE_HOLIDAY_MAX_GAP = 14
MIN_PAYOFF_DAYS = 4


@dataclass(slots=True, frozen=True)
class CandidateConstraints:
    """Constraints applied when selecting viable candidate windows."""

    blackout_ranges: tuple[tuple[date, date], ...]
    min_block_len: int | None
    max_block_len: int | None

    def allows_range(self, start: date, end: date) -> bool:
        if self.min_block_len and (end - start).days + 1 < self.min_block_len:
            return False
        if self.max_block_len and (end - start).days + 1 > self.max_block_len:
            return False
        return not any(overlaps_range(start, end, rng_start, rng_end) for rng_start, rng_end in self.blackout_ranges)


@dataclass(slots=True, frozen=True)
class CandidateConfig:
    """Configuration for generating candidate windows."""

    constraints: CandidateConstraints


def overlaps_range(a_start: date, a_end: date, b_start: date, b_end: date) -> bool:
    """Return True if two inclusive ranges overlap."""

    return not (a_end < b_start or a_start > b_end)


def expand_range(center: date, radius: int, year: int) -> tuple[date, date]:
    start = max(date(year, 1, 1), center - timedelta(days=radius))
    end = min(date(year, 12, 31), center + timedelta(days=radius))
    return start, end


def iter_dates(start: date, end: date) -> Iterator[date]:
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def generate_candidates(
    days: Sequence[DayInfo],
    config: CandidateConfig,
) -> list[CandidateWindow]:
    """Return PTO candidate windows seeded around holidays and weekends."""

    by_date = {info.day: info for info in days}
    year = days[0].day.year if days else date.today().year
    holidays = sorted(d.day for d in days if d.kind == DayType.HOLIDAY)
    weekends = sorted(d.day for d in days if d.kind == DayType.WEEKEND)

    windows: set[tuple[date, date]] = set()

    for holiday in holidays:
        windows.add(expand_range(holiday, WINDOW_RADIUS, year))

    for weekend_day in weekends:
        # Focus around Saturdays to avoid duplicates
        if weekend_day.weekday() == 5:  # Saturday
            windows.add(expand_range(weekend_day, 4, year))

    for idx, first in enumerate(holidays):
        for second in holidays[idx + 1 :]:
            if (second - first).days <= DOUBLE_HOLIDAY_MAX_GAP:
                windows.add((first, second))
            else:
                break

    candidates: list[CandidateWindow] = []
    for start, end in sorted(windows):
        if not config.constraints.allows_range(start, end):
            continue
        window_days = list(iter_dates(start, end))
        if len(window_days) < MIN_PAYOFF_DAYS:
            continue
        holidays_in_window: list[date] = []
        weekends_in_window: list[date] = []
        workdays_in_window: list[date] = []
        for day in window_days:
            info = by_date.get(day)
            if not info:
                continue
            if info.kind == DayType.WEEKEND:
                weekends_in_window.append(day)
            elif info.kind == DayType.HOLIDAY:
                holidays_in_window.append(day)
            else:
                workdays_in_window.append(day)
        pto_needed = len(workdays_in_window)
        if pto_needed == len(window_days):
            # No existing weekends/holidays; skip low value windows
            continue
        candidates.append(
            CandidateWindow(
                start=start,
                end=end,
                pto_needed=pto_needed,
                off_streak=len(window_days),
                holidays=tuple(sorted(holidays_in_window)),
                weekends=tuple(sorted(weekends_in_window)),
                workdays=tuple(sorted(workdays_in_window)),
            )
        )
    return sorted(
        candidates,
        key=lambda c: (c.end, c.start, c.pto_needed, c.off_streak),
    )


__all__ = [
    "CandidateConfig",
    "CandidateConstraints",
    "generate_candidates",
]
