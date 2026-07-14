"""Unit tests for certs.pin (SPKI pin comparison)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from certs.parser import spki_sha256
from certs.pin import pin_match


def _cert(now):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "pin.example.com")])
    return (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=1))
        .sign(key, hashes.SHA256())
    )


def test_pin_match_none_when_unconfigured():
    cert = _cert(datetime.now(timezone.utc))
    assert pin_match(cert, None) is None
    assert pin_match(cert, []) is None


def test_pin_match_true_when_expected_present():
    cert = _cert(datetime.now(timezone.utc))
    expected = [spki_sha256(cert)]
    assert pin_match(cert, expected) is True


def test_pin_match_false_when_mismatched():
    cert = _cert(datetime.now(timezone.utc))
    assert pin_match(cert, ["0" * 64]) is False
