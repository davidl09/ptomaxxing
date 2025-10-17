"""Module placeholder exposing application configuration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .api.routes_plan import compute_plan
from .core.config import get_settings

settings = get_settings()


@dataclass
class MockFastAPI:
    title: str

    def include_router(self, *_args: Any, **_kwargs: Any) -> None:  # pragma: no cover
        return None

    def get(self, *_args: Any, **_kwargs: Any) -> Callable:
        def decorator(func: Callable) -> Callable:
            return func

        return decorator


app = MockFastAPI(title=settings.app_name)


@app.get("/healthz")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


__all__ = ["app", "compute_plan"]
