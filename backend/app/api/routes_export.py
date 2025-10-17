"""ICS export endpoints."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from ..domain.models import PlanBlock
from ..services.ics_export import build_ics_document

router = object()


@dataclass
class ExportRequest:
    timezone: str
    title: str
    blocks: List[PlanBlock] = field(default_factory=list)


def export_ics(request: ExportRequest) -> bytes:
    """Return an ICS document for the provided blocks."""

    return build_ics_document(request.title, request.timezone, request.blocks)


__all__ = ["ExportRequest", "export_ics"]
