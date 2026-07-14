"""Data models for normalized certificate records (Milestone 1, design doc Section 11).

Note on `domain`: the design doc's CertificateRecord table (Section 11) does not
list a `domain` field, but `hostname_match` is defined as "vs. the domain being
watched" and the API spec (Section 12) filters `/api/certificates?domain=`.
Since the doc leaves the fixture format ("reconciled against starter repo on
receipt") and domain linkage unspecified, and no starter repo materialized, we
carry `domain` on the record as the minimal addition needed to make the
documented behavior implementable -- not an extra feature, just the missing
plumbing the doc's own API/hostname-match language requires.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ExpiryStatus(str, Enum):
    VALID = "valid"
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"


@dataclass
class CertificateRecord:
    id: str
    domain: str | None
    subject: str
    issuer: str
    fingerprint_sha256: str
    fingerprint_sha1: str
    not_before: datetime
    not_after: datetime
    expiry_status: ExpiryStatus
    hostnames: list[str]
    hostname_match: bool
    chain_valid: bool
    spki_pin_match: bool | None


@dataclass
class ParseError:
    domain: str | None
    fixture_id: str | None
    reason: str


class Severity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class Rule(str, Enum):
    EXPIRED = "expired"
    EXPIRING_SOON = "expiring_soon"
    HOSTNAME_MISMATCH = "hostname_mismatch"
    CHAIN_BROKEN = "chain_broken"
    PIN_MISMATCH = "pin_mismatch"


@dataclass
class PolicyFinding:
    domain: str | None
    certificate_id: str
    rule: Rule
    severity: Severity
    message: str
