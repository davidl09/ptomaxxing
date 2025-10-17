from datetime import date

from backend.app.domain.calendar_builder import CalendarConfig, build_calendar
from backend.app.domain.candidates import CandidateConfig, CandidateConstraints, generate_candidates


def test_generate_candidates_bridges_between_holidays() -> None:
    calendar = build_calendar(
        CalendarConfig(year=2024, weekend_days=(5, 6), country="US", region="US-CA")
    )
    constraints = CandidateConstraints(blackout_ranges=tuple(), min_block_len=None, max_block_len=None)
    candidates = generate_candidates(calendar, CandidateConfig(constraints=constraints))
    assert candidates
    july_candidates = [c for c in candidates if date(2024, 7, 4) >= c.start and date(2024, 7, 4) <= c.end]
    assert july_candidates, "expected window covering July 4th"
    for candidate in july_candidates:
        assert candidate.pto_needed < candidate.off_streak
