"""Unit tests for certs.chain (DN-based issuer/subject linking, design doc Section 13)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from certs.chain import validate_chain


def _cert(subject_cn, issuer_cn, now):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, subject_cn)])
    issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, issuer_cn)])
    return (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=1))
        .sign(key, hashes.SHA256())
    )


def test_chain_valid_when_issuer_present_in_pool():
    now = datetime.now(timezone.utc)
    root = _cert("Root", "Root", now)
    leaf = _cert("leaf.example.com", "Root", now)
    assert validate_chain(leaf, [leaf, root]) is True


def test_chain_broken_when_issuer_missing():
    now = datetime.now(timezone.utc)
    leaf = _cert("leaf.example.com", "Missing Root", now)
    assert validate_chain(leaf, [leaf]) is False


def test_self_signed_root_is_its_own_valid_chain():
    now = datetime.now(timezone.utc)
    root = _cert("Root", "Root", now)
    assert validate_chain(root, [root]) is True
