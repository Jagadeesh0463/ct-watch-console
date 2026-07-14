"""JSON serialization helpers for CertificateRecord / PolicyFinding (Milestone 2).

Dataclasses hold Enum and datetime fields that aren't JSON-serializable as-is;
these helpers convert them to the plain str values the API spec (design doc
Section 12) expects in responses.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from enum import Enum
from typing import Any


def _to_json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _to_json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_json_safe(v) for v in value]
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def record_to_dict(record: Any) -> dict:
    return _to_json_safe(asdict(record))


def finding_to_dict(finding: Any) -> dict:
    return _to_json_safe(asdict(finding))
