"""SPKI pin comparison (RFC 7469-style, design doc Section 13: pin_mismatch)."""

from __future__ import annotations

from cryptography import x509

from .parser import spki_sha256


def pin_match(cert: x509.Certificate, expected_pins: list[str] | None) -> bool | None:
    """None if no pin is configured for the domain (design doc Section 11:
    "spki_pin_match: bool | null, null if no expected pin configured")."""
    if not expected_pins:
        return None
    return spki_sha256(cert) in {p.lower() for p in expected_pins}
