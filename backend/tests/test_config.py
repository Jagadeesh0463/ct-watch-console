"""Unit tests for config.Config (design doc Section 16: env-driven config)."""

from __future__ import annotations

from datetime import timezone

from config import Config


def test_from_env_defaults(monkeypatch):
    for var in (
        "FIXTURE_DIR",
        "EXPIRY_WARNING_DAYS",
        "REFERENCE_TIME",
        "LOG_LEVEL",
        "API_HOST",
        "API_PORT",
        "CORS_ORIGINS",
    ):
        monkeypatch.delenv(var, raising=False)

    config = Config.from_env()
    assert config.expiry_warning_days == 30
    assert config.log_level == "INFO"
    assert config.api_host == "0.0.0.0"
    assert config.api_port == 5000
    assert config.cors_origins == ["*"]
    assert config.reference_time.tzinfo is not None


def test_from_env_reads_overrides(monkeypatch):
    monkeypatch.setenv("FIXTURE_DIR", "/tmp/some-fixtures")
    monkeypatch.setenv("EXPIRY_WARNING_DAYS", "14")
    monkeypatch.setenv("REFERENCE_TIME", "2026-07-14T00:00:00")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("API_HOST", "127.0.0.1")
    monkeypatch.setenv("API_PORT", "8080")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000, http://localhost:5173")

    config = Config.from_env()
    assert config.fixture_dir == "/tmp/some-fixtures"
    assert config.expiry_warning_days == 14
    assert config.reference_time.year == 2026
    assert config.log_level == "DEBUG"
    assert config.api_host == "127.0.0.1"
    assert config.api_port == 8080
    assert config.cors_origins == ["http://localhost:3000", "http://localhost:5173"]


def test_reference_time_naive_value_assumed_utc(monkeypatch):
    monkeypatch.setenv("REFERENCE_TIME", "2026-07-14T00:00:00")
    config = Config.from_env()
    assert config.reference_time.tzinfo == timezone.utc


def test_reference_time_aware_value_preserved(monkeypatch):
    monkeypatch.setenv("REFERENCE_TIME", "2026-07-14T00:00:00+05:30")
    config = Config.from_env()
    assert config.reference_time.utcoffset().total_seconds() == 5.5 * 3600
