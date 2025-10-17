"""Error helpers for API responses."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HTTPException(Exception):
    status_code: int
    detail: dict


def http_error(code: str, message: str, hint: str, *, status_code: int = 400) -> HTTPException:
    """Return a structured HTTP exception following the API contract."""

    return HTTPException(status_code=status_code, detail={"error": {"code": code, "message": message, "hint": hint}})


__all__ = ["HTTPException", "http_error"]
