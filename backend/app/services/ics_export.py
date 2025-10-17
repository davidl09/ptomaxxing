"""ICS export utilities for PTO plans."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Sequence
from uuid import uuid4

from zoneinfo import ZoneInfo

from ..domain.models import PlanBlock


def format_event(block: PlanBlock, timezone: str) -> str:
    tz = ZoneInfo(timezone)
    dtstamp = datetime.now(tz).strftime("%Y%m%dT%H%M%SZ")
    uid = f"max-days-off-{uuid4()}@fundsy"
    dtstart = block.start.strftime("%Y%m%d")
    dtend = (block.end + timedelta(days=1)).strftime("%Y%m%d")
    description_lines = ["PTO days:"] + [day.isoformat() for day in block.pto]
    if block.holidays:
        description_lines.append("Holidays:")
        description_lines.extend(day.isoformat() for day in block.holidays)
    description = "\\n".join(description_lines)
    return "\r\n".join(
        [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{dtstamp}",
            f"DTSTART;VALUE=DATE:{dtstart}",
            f"DTEND;VALUE=DATE:{dtend}",
            "SUMMARY:OOO — Break",
            "CATEGORIES:PTO,OutOfOffice",
            f"DESCRIPTION:{description}",
            "END:VEVENT",
        ]
    )


def build_ics_document(
    title: str,
    timezone: str,
    blocks: Sequence[PlanBlock],
) -> bytes:
    events = "\r\n".join(format_event(block, timezone) for block in blocks)
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Fundsy//Max Days Off//EN",
        f"X-WR-CALNAME:{title}",
        events,
        "END:VCALENDAR",
    ]
    return "\r\n".join(lines).encode("utf-8")


__all__ = ["build_ics_document"]
