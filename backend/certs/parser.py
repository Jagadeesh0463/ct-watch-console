"""PEM parsing, fingerprints, SPKI extraction, expiry status (Milestone 1)."""

from __future__ import annotations

import hashlib
from datetime import datetime

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization

from .models import ExpiryStatus


class CertificateParseError(Exception):
    """Raised when a PEM block cannot be parsed as an X.509 certificate."""


def parse_pem(pem_bytes: bytes) -> x509.Certificate:
    try:
        return x509.load_pem_x509_certificate(pem_bytes)
    except ValueError as exc:
        raise CertificateParseError(str(exc)) from exc


def fingerprints(cert: x509.Certificate) -> tuple[str, str]:
    sha256 = cert.fingerprint(hashes.SHA256()).hex()
    sha1 = cert.fingerprint(hashes.SHA1()).hex()
    return sha256, sha1


def spki_sha256(cert: x509.Certificate) -> str:
    spki_der = cert.public_key().public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return hashlib.sha256(spki_der).hexdigest()


def name_to_str(name: x509.Name) -> str:
    return name.rfc4514_string()


def compute_expiry_status(
    not_before: datetime,
    not_after: datetime,
    reference_time: datetime,
    warning_days: int,
) -> ExpiryStatus:
    """Expiry precedence per design doc Section 13: expired takes priority over
    expiring-soon by construction (checked first), so the two are mutually
    exclusive rather than both firing near the boundary.
    """
    if reference_time.tzinfo is None:
        raise ValueError("reference_time must be timezone-aware (UTC)")
    if not_after < reference_time:
        return ExpiryStatus.EXPIRED
    if (not_after - reference_time).days <= warning_days:
        return ExpiryStatus.EXPIRING_SOON
    return ExpiryStatus.VALID
