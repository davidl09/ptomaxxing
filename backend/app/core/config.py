"""Application configuration using pydantic settings."""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    app_name: str = Field(default="Max Days Off API", alias="APP_NAME")
    app_timezone: str = Field(default="America/Toronto", alias="APP_TZ")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", alias="LOG_LEVEL"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        populate_by_name = True


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()  # type: ignore[call-arg]


__all__ = ["Settings", "get_settings"]
