"""Unit tests for certs.parser (PEM parsing, fingerprints, expiry status)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from certs.models import ExpiryStatus
from certs.parser import (
    CertificateParseError,
    compute_expiry_status,
    fingerprints,
    name_to_str,
    parse_pem,
    spki_sha256,
)


def _self_signed_cert(not_before, not_after):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "unit-test.example.com")])
    return (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(not_before)
        .not_valid_after(not_after)
        .sign(key, hashes.SHA256())
    )


def test_parse_pem_roundtrip():
    now = datetime.now(timezone.utc)
    cert = _self_signed_cert(now - timedelta(days=1), now + timedelta(days=1))
    pem = cert.public_bytes(serialization.Encoding.PEM)
    parsed = parse_pem(pem)
    assert name_to_str(parsed.subject) == name_to_str(cert.subject)


def test_parse_pem_invalid_raises():
    with pytest.raises(CertificateParseError):
        parse_pem(b"not a real cert")


def test_fingerprints_are_hex_and_distinct():
    now = datetime.now(timezone.utc)
    cert = _self_signed_cert(now - timedelta(days=1), now + timedelta(days=1))
    sha256, sha1 = fingerprints(cert)
    assert len(sha256) == 64
    assert len(sha1) == 40
    assert sha256 != sha1


def test_spki_sha256_stable_for_same_cert():
    now = datetime.now(timezone.utc)
    cert = _self_signed_cert(now - timedelta(days=1), now + timedelta(days=1))
    assert spki_sha256(cert) == spki_sha256(cert)


@pytest.mark.parametrize(
    "delta_before, delta_after, warning_days, expected",
    [
        (timedelta(days=-10), timedelta(days=300), 30, ExpiryStatus.VALID),
        (timedelta(days=-10), timedelta(days=10), 30, ExpiryStatus.EXPIRING_SOON),
        (timedelta(days=-400), timedelta(days=-30), 30, ExpiryStatus.EXPIRED),
        (timedelta(days=-10), timedelta(days=31), 30, ExpiryStatus.VALID),  # just past threshold
        (timedelta(days=-10), timedelta(days=30), 30, ExpiryStatus.EXPIRING_SOON),  # exact boundary
    ],
)
def test_compute_expiry_status(delta_before, delta_after, warning_days, expected):
    reference = datetime(2026, 7, 14, tzinfo=timezone.utc)
    not_before = reference + delta_before
    not_after = reference + delta_after
    assert compute_expiry_status(not_before, not_after, reference, warning_days) == expected


def test_compute_expiry_status_requires_aware_reference():
    with pytest.raises(ValueError):
        compute_expiry_status(datetime(2020, 1, 1), datetime(2030, 1, 1), datetime(2026, 7, 14), 30)
