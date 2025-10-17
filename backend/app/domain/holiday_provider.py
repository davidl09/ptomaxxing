"""Holiday provider with optional fallback when python-holidays is unavailable."""
from __future__ import annotations

from datetime import date
from typing import Dict, Iterable, Mapping, Tuple

FallbackCalendar = Mapping[Tuple[str, str | None, int], Dict[date, str]]

FALLBACK_HOLIDAYS: FallbackCalendar = {
    ("CA", "CA-ON", 2024): {
        date(2024, 1, 1): "New Year's Day",
        date(2024, 2, 19): "Family Day",
        date(2024, 3, 29): "Good Friday",
        date(2024, 5, 20): "Victoria Day",
        date(2024, 7, 1): "Canada Day",
        date(2024, 9, 2): "Labour Day",
        date(2024, 10, 14): "Thanksgiving",
        date(2024, 12, 25): "Christmas Day",
        date(2024, 12, 26): "Boxing Day",
    },
    ("US", "US-CA", 2024): {
        date(2024, 1, 1): "New Year's Day",
        date(2024, 5, 27): "Memorial Day",
        date(2024, 7, 4): "Independence Day",
        date(2024, 9, 2): "Labor Day",
        date(2024, 11, 28): "Thanksgiving Day",
        date(2024, 12, 25): "Christmas Day",
    },
    ("GB", "GB-ENG", 2024): {
        date(2024, 1, 1): "New Year's Day",
        date(2024, 4, 1): "Easter Monday",
        date(2024, 5, 6): "Early May Bank Holiday",
        date(2024, 12, 25): "Christmas Day",
        date(2024, 12, 26): "Boxing Day",
    },
    ("AU", "AU-NSW", 2024): {
        date(2024, 1, 1): "New Year's Day",
        date(2024, 1, 26): "Australia Day",
        date(2024, 4, 25): "ANZAC Day",
        date(2024, 12, 25): "Christmas Day",
        date(2024, 12, 26): "Boxing Day",
    },
}


def get_holidays(country: str, region: str | None, year: int) -> Dict[date, str]:
    """Return a holiday mapping, preferring python-holidays when available."""

    try:
        import holidays  # type: ignore

        calendar = holidays.country_holidays(country=country, subdiv=region, years=year, observed=True)
        return dict(calendar.items())
    except ModuleNotFoundError:
        return dict(FALLBACK_HOLIDAYS.get((country, region, year), {}))


__all__ = ["get_holidays"]
