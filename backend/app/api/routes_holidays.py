"""Holiday endpoint implementation."""
from __future__ import annotations

from typing import Optional

from ..core.locale import LocaleRequest
from ..domain.holiday_provider import get_holidays
from ..domain.models import HolidayModel

router = object()


def list_holidays(
    year: int,
    country: str,
    region: Optional[str] = None,
    timezone: Optional[str] = None,
) -> dict:
    """Return the observed holidays for the requested locale."""

    locale = LocaleRequest(country=country, region=region).normalize()
    country_holidays = get_holidays(locale.country, locale.region, year)
    payload = [
        HolidayModel(date=holiday_date, name=name, observed=True).to_dict()
        for holiday_date, name in sorted(country_holidays.items())
    ]
    return {
        "year": year,
        "country": locale.country,
        "region": locale.region,
        "timezone": timezone,
        "holidays": payload,
    }


__all__ = ["list_holidays"]
