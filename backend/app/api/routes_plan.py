"""Plan computation endpoint."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional, Sequence

from ..api.errors import http_error
from ..core.locale import LocaleRequest
from ..domain.calendar_builder import CalendarConfig, build_calendar
from ..domain.candidates import CandidateConfig, CandidateConstraints, generate_candidates
from ..domain.models import Plan, PlanBlock
from ..domain.scoring import Goal, PlanPreference, PreferenceConfig
from ..domain.selection import PlanCandidate, SelectionConfig, select_plans

router = object()  # placeholder for compatibility with FastAPI pattern

WEEKDAY_MAP = {
    "MON": 0,
    "TUE": 1,
    "WED": 2,
    "THU": 3,
    "FRI": 4,
    "SAT": 5,
    "SUN": 6,
}


@dataclass
class PreferenceInput:
    reserve_pto: int = 0
    season_spread: bool = False
    prefer_months: List[int] = field(default_factory=list)
    avoid_months: List[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        for month in [*self.prefer_months, *self.avoid_months]:
            if month < 1 or month > 12:
                raise ValueError("Month values must be between 1 and 12")

    def to_dict(self) -> dict:
        return {
            "reserve_pto": self.reserve_pto,
            "season_spread": self.season_spread,
            "prefer_months": list(self.prefer_months),
            "avoid_months": list(self.avoid_months),
        }


@dataclass
class ConstraintInput:
    blackouts: List[str] = field(default_factory=list)
    min_block_len: Optional[int] = None
    max_block_len: Optional[int] = None

    def __post_init__(self) -> None:
        for item in self.blackouts:
            if ".." not in item:
                raise ValueError("Blackout ranges must use '..' separator")

    def to_dict(self) -> dict:
        return {
            "blackouts": list(self.blackouts),
            "min_block_len": self.min_block_len,
            "max_block_len": self.max_block_len,
        }


@dataclass
class PlanRequest:
    year: int
    country: str
    region: Optional[str]
    timezone: str
    pto_total: int
    blocks_max: int
    weekend: List[str]
    goal: str
    prefs: PreferenceInput = field(default_factory=PreferenceInput)
    constraints: ConstraintInput = field(default_factory=ConstraintInput)

    def __post_init__(self) -> None:
        if self.year < 1900 or self.year > 2100:
            raise ValueError("year out of supported range")
        if self.blocks_max < 1 or self.blocks_max > 5:
            raise ValueError("blocks_max must be between 1 and 5")
        if self.pto_total < 0:
            raise ValueError("pto_total must be non-negative")
        normalized = []
        for day in self.weekend:
            code = day.upper()
            if code not in WEEKDAY_MAP:
                raise ValueError(f"Unknown weekday '{day}'")
            normalized.append(code)
        self.weekend = sorted(set(normalized))
        if self.goal not in (Goal.MAX_TOTAL.value, Goal.MAX_LONGEST.value):
            raise ValueError("Unknown goal")

    def weekend_indices(self) -> List[int]:
        return [WEEKDAY_MAP[day] for day in self.weekend]

    def blackout_ranges(self) -> tuple[tuple[date, date], ...]:
        ranges: list[tuple[date, date]] = []
        for item in self.constraints.blackouts:
            start_str, end_str = item.split("..")
            start = date.fromisoformat(start_str)
            end = date.fromisoformat(end_str)
            if end < start:
                raise ValueError("Blackout end must be after start")
            ranges.append((start, end))
        return tuple(ranges)

    def to_dict(self) -> dict:
        return {
            "year": self.year,
            "country": self.country,
            "region": self.region,
            "timezone": self.timezone,
            "pto_total": self.pto_total,
            "blocks_max": self.blocks_max,
            "weekend": list(self.weekend),
            "goal": self.goal,
            "prefs": self.prefs.to_dict(),
            "constraints": self.constraints.to_dict(),
        }


@dataclass
class PlanResponse:
    params: dict
    plans: Sequence[Plan]
    alternates: Sequence[Plan]

    def model_dump(self) -> dict:
        return {
            "params": self.params,
            "plans": [plan.to_dict() for plan in self.plans],
            "alternates": [plan.to_dict() for plan in self.alternates],
        }


def build_plan_block(candidate: PlanCandidate, window_index: int) -> PlanBlock:
    window = candidate.windows[window_index]
    explanation = (
        f"{window.start.isoformat()} to {window.end.isoformat()} — {window.off_streak} days off"
        f" using {window.pto_needed} PTO"
    )
    return PlanBlock(
        start=window.start,
        end=window.end,
        days_off=window.off_streak,
        pto=list(window.workdays),
        holidays=list(window.holidays),
        weekends=list(window.weekends),
        explain=explanation,
    )


def candidate_to_plan(candidate: PlanCandidate) -> Plan:
    blocks = [build_plan_block(candidate, idx) for idx in range(len(candidate.windows))]
    return Plan(score=candidate.score, pto_used=candidate.pto_used, blocks=blocks)


async def compute_plan(request: PlanRequest) -> PlanResponse:
    locale = LocaleRequest(country=request.country, region=request.region).normalize()
    reserve = request.prefs.reserve_pto or 0
    if reserve > request.pto_total:
        raise http_error(
            "INVALID_INPUT",
            "Reserve exceeds PTO total",
            "Reduce reserve PTO or increase total",
        )
    available_pto = max(0, request.pto_total - reserve)

    calendar = build_calendar(
        CalendarConfig(
            year=request.year,
            weekend_days=request.weekend_indices(),
            country=locale.country,
            region=locale.region,
        )
    )

    candidate_constraints = CandidateConstraints(
        blackout_ranges=request.blackout_ranges(),
        min_block_len=request.constraints.min_block_len,
        max_block_len=request.constraints.max_block_len,
    )
    candidates = generate_candidates(
        calendar,
        CandidateConfig(constraints=candidate_constraints),
    )

    if not candidates:
        return PlanResponse(params=request.to_dict(), plans=[], alternates=[])

    preference = PreferenceConfig(
        penalty_lambda=0.25,
        prefer_months=frozenset(request.prefs.prefer_months),
        avoid_months=frozenset(request.prefs.avoid_months),
    )
    plan_pref = PlanPreference(goal=Goal(request.goal), season_spread=request.prefs.season_spread)
    selection = select_plans(
        candidates,
        SelectionConfig(
            budget=available_pto,
            blocks_max=request.blocks_max,
            top_k=5,
            prefs=preference,
            plan_prefs=plan_pref,
        ),
    )

    plans = [candidate_to_plan(candidate) for candidate in selection[:3]]
    alternates = [candidate_to_plan(candidate) for candidate in selection[3:]]
    return PlanResponse(
        params=request.to_dict(),
        plans=plans,
        alternates=alternates,
    )


__all__ = ["PlanRequest", "PlanResponse", "PreferenceInput", "ConstraintInput", "compute_plan"]
