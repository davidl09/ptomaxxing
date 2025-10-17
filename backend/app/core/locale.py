"""Locale utilities for normalizing country and region codes."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class NormalizedLocale:
    country: str
    region: Optional[str]


@dataclass
class LocaleRequest:
    country: str
    region: Optional[str] = None

    def normalize(self) -> NormalizedLocale:
        country_code = self.country.upper()
        region_code: Optional[str]
        if self.region:
            raw_region = self.region.upper().replace(" ", "")
            if "-" in raw_region:
                region_code = raw_region
            else:
                region_code = f"{country_code}-{raw_region}"
        else:
            region_code = None
        return NormalizedLocale(country=country_code, region=region_code)


__all__ = ["LocaleRequest", "NormalizedLocale"]
