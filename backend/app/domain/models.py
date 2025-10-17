"""Domain models for the Max Days Off planner."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Sequence


class DayType(str, Enum):
    WORKDAY = "workday"
    HOLIDAY = "holiday"
    WEEKEND = "weekend"


@dataclass(slots=True, frozen=True)
class DayInfo:
    day: date
    kind: DayType
    name: str | None = None


@dataclass(slots=True, frozen=True)
class CandidateWindow:
    start: date
    end: date
    pto_needed: int
    off_streak: int
    holidays: tuple[date, ...]
    weekends: tuple[date, ...]
    workdays: tuple[date, ...]

    def overlaps(self, other: "CandidateWindow") -> bool:
        return not (self.end < other.start or self.start > other.end)


@dataclass(slots=True)
class HolidayModel:
    date: date
    name: str
    observed: bool = True

    def to_dict(self) -> dict:
        return {"date": self.date.isoformat(), "name": self.name, "observed": self.observed}


@dataclass(slots=True)
class PlanBlock:
    start: date
    end: date
    days_off: int
    pto: List[date] = field(default_factory=list)
    holidays: List[date] = field(default_factory=list)
    weekends: List[date] = field(default_factory=list)
    explain: str = ""

    def __post_init__(self) -> None:
        self.pto.sort()
        self.holidays.sort()
        self.weekends.sort()

    def to_dict(self) -> dict:
        return {
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "days_off": self.days_off,
            "pto": [day.isoformat() for day in self.pto],
            "holidays": [day.isoformat() for day in self.holidays],
            "weekends": [day.isoformat() for day in self.weekends],
            "explain": self.explain,
        }


@dataclass(slots=True)
class Plan:
    score: float
    pto_used: int
    blocks: Sequence[PlanBlock]

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "pto_used": self.pto_used,
            "blocks": [block.to_dict() for block in self.blocks],
        }


__all__ = [
    "DayInfo",
    "DayType",
    "CandidateWindow",
    "HolidayModel",
    "PlanBlock",
    "Plan",
]
