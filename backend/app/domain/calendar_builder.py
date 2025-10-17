"""Utilities for constructing labeled calendars for the planning horizon."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable, Iterator, Mapping, Sequence

from .holiday_provider import get_holidays
from .models import DayInfo, DayType


@dataclass(frozen=True)
class CalendarConfig:
    """Configuration input for building the day grid."""

    year: int
    weekend_days: Sequence[int]
    country: str
    region: str | None


def iter_year_days(year: int) -> Iterator[date]:
    """Yield each date within the calendar year."""

    current = date(year, 1, 1)
    end = date(year, 12, 31)
    while current <= end:
        yield current
        current += timedelta(days=1)


def build_calendar(config: CalendarConfig) -> list[DayInfo]:
    """Label every day of the requested year with weekend and holiday metadata."""

    country_holidays = get_holidays(config.country, config.region, config.year)
    weekend_set = frozenset(config.weekend_days)

    result: list[DayInfo] = []
    for current in iter_year_days(config.year):
        if current.weekday() in weekend_set:
            result.append(DayInfo(day=current, kind=DayType.WEEKEND, name=None))
            continue
        holiday_name = country_holidays.get(current)
        if holiday_name:
            result.append(DayInfo(day=current, kind=DayType.HOLIDAY, name=holiday_name))
        else:
            result.append(DayInfo(day=current, kind=DayType.WORKDAY, name=None))
    return result


def index_by_date(days: Iterable[DayInfo]) -> Mapping[date, DayInfo]:
    """Return a mapping from date to DayInfo for quick lookup."""

    return {item.day: item for item in days}


__all__ = ["CalendarConfig", "build_calendar", "index_by_date"]
