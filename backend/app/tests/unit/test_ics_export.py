from datetime import date

from backend.app.domain.models import PlanBlock
from backend.app.services.ics_export import build_ics_document


def test_build_ics_document_contains_summary() -> None:
    block = PlanBlock(
        start=date(2024, 5, 1),
        end=date(2024, 5, 5),
        days_off=5,
        pto=[date(2024, 5, 2), date(2024, 5, 3)],
        holidays=[date(2024, 5, 1)],
        weekends=[date(2024, 5, 4), date(2024, 5, 5)],
        explain="Test block",
    )
    payload = build_ics_document("Test", "America/Toronto", [block])
    assert b"SUMMARY:OOO \xe2\x80\x94 Break" in payload
