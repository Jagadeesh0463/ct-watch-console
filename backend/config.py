"""Environment-driven configuration (design doc Section 16). No hardcoded
values -- every setting is overridable via env var, 12-factor style.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_FIXTURE_DIR = str(Path(__file__).parent / "fixtures")


def _parse_reference_time(value: str | None) -> datetime:
    """REFERENCE_TIME overrides "now" for deterministic tests/runs (design doc
    Section 16). Falls back to the real current time when unset."""
    if not value:
        return datetime.now(timezone.utc)
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _parse_cors_origins(value: str) -> list[str]:
    return [origin.strip() for origin in value.split(",") if origin.strip()]


@dataclass
class Config:
    fixture_dir: str = DEFAULT_FIXTURE_DIR
    expiry_warning_days: int = 30
    reference_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 5000
    cors_origins: list[str] = field(default_factory=lambda: ["*"])

    @classmethod
    def from_env(cls) -> Config:
        return cls(
            fixture_dir=os.environ.get("FIXTURE_DIR", DEFAULT_FIXTURE_DIR),
            expiry_warning_days=int(os.environ.get("EXPIRY_WARNING_DAYS", "30")),
            reference_time=_parse_reference_time(os.environ.get("REFERENCE_TIME")),
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
            api_host=os.environ.get("API_HOST", "0.0.0.0"),
            api_port=int(os.environ.get("API_PORT", "5000")),
            cors_origins=_parse_cors_origins(os.environ.get("CORS_ORIGINS", "*")),
        )
