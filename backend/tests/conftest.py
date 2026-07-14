"""Shared pytest fixtures for Milestone 1 tests."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures"
SAMPLE_FIXTURE_PATH = FIXTURE_DIR / "sample_fixtures.json"


def _meta() -> dict:
    return json.loads(SAMPLE_FIXTURE_PATH.read_text())["_meta"]


@pytest.fixture(scope="session")
def reference_time() -> datetime:
    return datetime.fromisoformat(_meta()["reference_time"])


@pytest.fixture(scope="session")
def warning_days() -> int:
    return _meta()["warning_days"]


@pytest.fixture(scope="session")
def fixture_dir() -> Path:
    return FIXTURE_DIR
