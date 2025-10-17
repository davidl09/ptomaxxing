"""Selection logic for assembling non-overlapping PTO plans."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .models import CandidateWindow
from .scoring import PlanPreference, PreferenceConfig, plan_score, score_candidate


@dataclass(slots=True, frozen=True)
class PlanCandidate:
    windows: tuple[CandidateWindow, ...]
    base_scores: tuple[float, ...]
    pto_used: int
    score: float

    def to_summary(self) -> tuple:
        return tuple((window.start, window.end) for window in self.windows)


@dataclass(slots=True, frozen=True)
class SelectionConfig:
    budget: int
    blocks_max: int
    top_k: int
    prefs: PreferenceConfig
    plan_prefs: PlanPreference


def select_plans(candidates: Sequence[CandidateWindow], config: SelectionConfig) -> list[PlanCandidate]:
    """Return the top plans abiding by PTO budget and block limits."""

    if not candidates:
        return []

    scored = [score_candidate(candidate, config.prefs) for candidate in candidates]

    states: dict[tuple[tuple[CandidateWindow, ...], int], PlanCandidate] = {}
    base_state = PlanCandidate(windows=tuple(), base_scores=tuple(), pto_used=0, score=0.0)
    states[(base_state.windows, base_state.pto_used)] = base_state

    for candidate, base_score in zip(candidates, scored):
        snapshot = list(states.values())
        for state in snapshot:
            if state.windows and state.windows[-1].end >= candidate.start:
                if candidate.start <= state.windows[-1].end:
                    continue
            total_pto = state.pto_used + candidate.pto_needed
            if total_pto > config.budget:
                continue
            if len(state.windows) + 1 > config.blocks_max:
                continue
            new_windows = state.windows + (candidate,)
            new_base_scores = state.base_scores + (base_score,)
            new_score = plan_score(new_windows, config.plan_prefs, new_base_scores)
            key = (new_windows, total_pto)
            existing = states.get(key)
            if existing is None or new_score > existing.score:
                states[key] = PlanCandidate(
                    windows=new_windows,
                    base_scores=new_base_scores,
                    pto_used=total_pto,
                    score=new_score,
                )

    plans = [state for state in states.values() if state.windows]
    plans.sort(
        key=lambda plan: (
            -plan.score,
            -sum(window.off_streak for window in plan.windows),
            plan.to_summary(),
        )
    )
    return plans[: config.top_k]


__all__ = ["PlanCandidate", "SelectionConfig", "select_plans"]
