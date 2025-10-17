from datetime import date

from backend.app.domain.models import CandidateWindow
from backend.app.domain.scoring import Goal, PlanPreference, PreferenceConfig
from backend.app.domain.selection import SelectionConfig, select_plans


def window(start_day: int, end_day: int, pto: int, off: int) -> CandidateWindow:
    return CandidateWindow(
        start=date(2024, 5, start_day),
        end=date(2024, 5, end_day),
        pto_needed=pto,
        off_streak=off,
        holidays=tuple(),
        weekends=tuple(),
        workdays=tuple(date(2024, 5, d) for d in range(start_day, end_day + 1))[:pto],
    )


def test_select_plans_enforces_non_overlap() -> None:
    candidates = [
        window(1, 5, 2, 5),
        window(6, 10, 3, 5),
        window(3, 8, 4, 6),
    ]
    plans = select_plans(
        candidates,
        SelectionConfig(
            budget=5,
            blocks_max=2,
            top_k=3,
            prefs=PreferenceConfig(),
            plan_prefs=PlanPreference(goal=Goal.MAX_TOTAL, season_spread=True),
        ),
    )
    assert plans
    for plan in plans:
        assert len(plan.windows) <= 2
        for first, second in zip(plan.windows, plan.windows[1:]):
            assert first.end < second.start
        assert plan.pto_used <= 5
