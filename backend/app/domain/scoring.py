"""Scoring helpers for candidate windows and plans."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Iterable, Sequence

from .models import CandidateWindow


class Goal(str, Enum):
    """Primary optimization goals supported by the planner."""

    MAX_TOTAL = "max_total"
    MAX_LONGEST = "max_longest"


@dataclass(slots=True, frozen=True)
class PreferenceConfig:
    """Preferences that influence scoring of windows."""

    penalty_lambda: float = 0.25
    prefer_months: frozenset[int] = frozenset()
    avoid_months: frozenset[int] = frozenset()

    def month_weight(self, month: int) -> float:
        if month in self.prefer_months:
            return 1.0
        if month in self.avoid_months:
            return -1.0
        return 0.0


@dataclass(slots=True, frozen=True)
class PlanPreference:
    """Plan level knobs used when selecting final windows."""

    goal: Goal
    season_spread: bool


def score_candidate(window: CandidateWindow, prefs: PreferenceConfig) -> float:
    """Return the base score for a single candidate window."""

    base = float(window.off_streak)
    penalty = prefs.penalty_lambda * float(window.pto_needed)
    month_values = sum(prefs.month_weight(day.month) for day in window.workdays)
    density_bonus = float(window.off_streak) / float(max(1, window.pto_needed))
    return base - penalty + 0.1 * month_values + 0.05 * density_bonus


def seasonal_bonus(windows: Sequence[CandidateWindow]) -> float:
    """Reward windows that span multiple quarters."""

    if not windows:
        return 0.0
    quarters = {((window.start.month - 1) // 3) + 1 for window in windows}
    return 1.5 * (len(quarters) - 1)


def plan_score(windows: Sequence[CandidateWindow], prefs: PlanPreference, base_scores: Iterable[float]) -> float:
    """Compute the aggregate plan score."""

    total = sum(base_scores)
    if prefs.goal == Goal.MAX_LONGEST and windows:
        longest = max(windows, key=lambda w: w.off_streak)
        total += longest.off_streak * 0.1
    if prefs.season_spread:
        total += seasonal_bonus(windows)
    return total


__all__ = ["Goal", "PreferenceConfig", "PlanPreference", "score_candidate", "plan_score"]
