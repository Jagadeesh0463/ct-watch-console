"""Fixture loading (design doc Section 15: malformed fixture handling)."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def load_fixture_dir(fixture_dir: str | Path) -> list[dict[str, Any]]:
    """Read every *.json file in fixture_dir, returning a flat list of domain blocks.

    A malformed JSON file is logged and skipped rather than raising, per the
    design doc's error-handling table (Section 15: "Malformed fixture JSON ->
    Log + skip entry, surface as a load_error finding rather than crashing").
    """
    fixture_dir = Path(fixture_dir)
    domains: list[dict[str, Any]] = []
    for path in sorted(fixture_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            logger.error("Skipping malformed fixture file %s: %s", path, exc)
            continue
        for domain_block in data.get("domains", []):
            domains.append(domain_block)
    return domains
