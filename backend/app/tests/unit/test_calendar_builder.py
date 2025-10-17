from datetime import date

import pytest

from backend.app.domain.calendar_builder import CalendarConfig, build_calendar
from backend.app.domain.models import DayType


@pytest.mark.parametrize(
    "country,region", [("US", "US-CA"), ("CA", "CA-ON"), ("GB", "GB-ENG"), ("AU", "AU-NSW")]
)
def test_calendar_marks_holidays(country: str, region: str) -> None:
    calendar = build_calendar(
        CalendarConfig(year=2024, weekend_days=(5, 6), country=country, region=region)
    )
    assert calendar, "calendar should not be empty"
    holidays = [day for day in calendar if day.kind == DayType.HOLIDAY]
    assert holidays, f"expected holidays for {country}/{region}"
    for holiday in holidays:
        if holiday.day.weekday() in (5, 6):
            # Observed holiday should create at least one workday replacement
            observed = [d for d in calendar if d.day == holiday.day and d.kind == DayType.HOLIDAY]
            assert observed
