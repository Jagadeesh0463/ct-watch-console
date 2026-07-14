"""Generates deterministic synthetic CT-style fixtures for Milestone 1.

No starter repo/fixtures were provided, so this generates them: real X.509
certs built with `cryptography`, covering every edge case in the Milestone 1
acceptance criteria (valid / expiring-soon / expired, hostname match/mismatch
incl. wildcard, broken chain, pin match/mismatch/unconfigured, malformed
entry, self-signed-root-only chain). Uses a fixed reference time so re-running
produces the same domain/edge-case coverage (key material and serials are
still randomly generated each run -- that's fine, tests read the reference
time back from the file rather than assuming byte-identical output).
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

REFERENCE_TIME = datetime(2026, 7, 14, tzinfo=timezone.utc)
WARNING_DAYS = 30
OUT_PATH = Path(__file__).parent / "sample_fixtures.json"


def _make_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _name(cn: str) -> x509.Name:
    return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])


def _build_cert(subject_cn, issuer_cn, signing_key, subject_key, not_before, not_after, sans=None):
    builder = (
        x509.CertificateBuilder()
        .subject_name(_name(subject_cn))
        .issuer_name(_name(issuer_cn))
        .public_key(subject_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(not_before)
        .not_valid_after(not_after)
    )
    if sans:
        builder = builder.add_extension(
            x509.SubjectAlternativeName([x509.DNSName(s) for s in sans]), critical=False
        )
    return builder.sign(signing_key, hashes.SHA256())


def _pem(cert: x509.Certificate) -> str:
    return cert.public_bytes(serialization.Encoding.PEM).decode()


def _spki_sha256(cert: x509.Certificate) -> str:
    der = cert.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return hashlib.sha256(der).hexdigest()


def build() -> dict:
    domains = []
    T = REFERENCE_TIME

    # 1. Fully valid chain: root -> intermediate -> leaf, pin configured and matching.
    root_key = _make_key()
    root = _build_cert(
        "Root CA 1",
        "Root CA 1",
        root_key,
        root_key,
        T - timedelta(days=3650),
        T + timedelta(days=3650),
    )
    inter_key = _make_key()
    inter = _build_cert(
        "Intermediate CA 1",
        "Root CA 1",
        root_key,
        inter_key,
        T - timedelta(days=365),
        T + timedelta(days=365),
    )
    leaf_key = _make_key()
    leaf = _build_cert(
        "valid.example.com",
        "Intermediate CA 1",
        inter_key,
        leaf_key,
        T - timedelta(days=10),
        T + timedelta(days=300),
        sans=["valid.example.com"],
    )
    domains.append(
        {
            "domain": "valid.example.com",
            "expected_spki_pins": [_spki_sha256(leaf)],
            "certificates": [
                {"id": "valid-leaf", "pem": _pem(leaf)},
                {"id": "valid-intermediate", "pem": _pem(inter)},
                {"id": "valid-root", "pem": _pem(root)},
            ],
        }
    )

    # 2. Expired leaf.
    leaf2_key = _make_key()
    leaf2 = _build_cert(
        "expired.example.com",
        "Root CA 1",
        root_key,
        leaf2_key,
        T - timedelta(days=400),
        T - timedelta(days=30),
        sans=["expired.example.com"],
    )
    domains.append(
        {
            "domain": "expired.example.com",
            "certificates": [
                {"id": "expired-leaf", "pem": _pem(leaf2)},
                {"id": "expired-root", "pem": _pem(root)},
            ],
        }
    )

    # 3. Expiring soon (within WARNING_DAYS).
    leaf3_key = _make_key()
    leaf3 = _build_cert(
        "expiring-soon.example.com",
        "Root CA 1",
        root_key,
        leaf3_key,
        T - timedelta(days=60),
        T + timedelta(days=10),
        sans=["expiring-soon.example.com"],
    )
    domains.append(
        {
            "domain": "expiring-soon.example.com",
            "certificates": [
                {"id": "expiring-leaf", "pem": _pem(leaf3)},
                {"id": "expiring-root", "pem": _pem(root)},
            ],
        }
    )

    # 4. Hostname mismatch: SAN doesn't include the watched domain.
    leaf4_key = _make_key()
    leaf4 = _build_cert(
        "mismatch.example.com",
        "Root CA 1",
        root_key,
        leaf4_key,
        T - timedelta(days=10),
        T + timedelta(days=300),
        sans=["other-name.example.com"],
    )
    domains.append(
        {
            "domain": "mismatch.example.com",
            "certificates": [
                {"id": "mismatch-leaf", "pem": _pem(leaf4)},
                {"id": "mismatch-root", "pem": _pem(root)},
            ],
        }
    )

    # 5. Wildcard SAN correctly matches a one-label subdomain.
    leaf5_key = _make_key()
    leaf5 = _build_cert(
        "sub.wildcard.example.com",
        "Root CA 1",
        root_key,
        leaf5_key,
        T - timedelta(days=10),
        T + timedelta(days=300),
        sans=["*.wildcard.example.com"],
    )
    domains.append(
        {
            "domain": "sub.wildcard.example.com",
            "certificates": [
                {"id": "wildcard-leaf", "pem": _pem(leaf5)},
                {"id": "wildcard-root", "pem": _pem(root)},
            ],
        }
    )

    # 6. Broken chain: the issuer ("Intermediate CA Orphan") signs the leaf but
    # its own cert is intentionally left out of the pool below.
    orphan_inter_key = _make_key()
    leaf6_key = _make_key()
    leaf6 = _build_cert(
        "broken-chain.example.com",
        "Intermediate CA Orphan",
        orphan_inter_key,
        leaf6_key,
        T - timedelta(days=10),
        T + timedelta(days=300),
        sans=["broken-chain.example.com"],
    )
    domains.append(
        {
            "domain": "broken-chain.example.com",
            "certificates": [
                {"id": "broken-leaf", "pem": _pem(leaf6)},
                # "Root CA Missing" deliberately omitted from the pool.
            ],
        }
    )

    # 7. Pin mismatch: expected pin configured but doesn't match the leaf's SPKI.
    leaf7_key = _make_key()
    leaf7 = _build_cert(
        "pin-mismatch.example.com",
        "Root CA 1",
        root_key,
        leaf7_key,
        T - timedelta(days=10),
        T + timedelta(days=300),
        sans=["pin-mismatch.example.com"],
    )
    domains.append(
        {
            "domain": "pin-mismatch.example.com",
            "expected_spki_pins": ["0" * 64],
            "certificates": [
                {"id": "pin-mismatch-leaf", "pem": _pem(leaf7)},
                {"id": "pin-mismatch-root", "pem": _pem(root)},
            ],
        }
    )

    # 8. Malformed entry: not valid PEM, should become a ParseError, not a record.
    domains.append(
        {
            "domain": "malformed.example.com",
            "certificates": [
                {
                    "id": "malformed-cert",
                    "pem": "-----BEGIN CERTIFICATE-----\nNOTVALIDBASE64\n-----END CERTIFICATE-----",
                },
            ],
        }
    )

    # 9. Self-signed root only, no intermediate -- chain should still validate.
    selfsigned_key = _make_key()
    selfsigned = _build_cert(
        "selfsigned.example.com",
        "selfsigned.example.com",
        selfsigned_key,
        selfsigned_key,
        T - timedelta(days=10),
        T + timedelta(days=300),
        sans=["selfsigned.example.com"],
    )
    domains.append(
        {
            "domain": "selfsigned.example.com",
            "certificates": [
                {"id": "selfsigned-leaf", "pem": _pem(selfsigned)},
            ],
        }
    )

    return {
        "_meta": {"reference_time": REFERENCE_TIME.isoformat(), "warning_days": WARNING_DAYS},
        "domains": domains,
    }


def main() -> None:
    data = build()
    OUT_PATH.write_text(json.dumps(data, indent=2))
    print(f"Wrote {OUT_PATH} ({len(data['domains'])} domains)")


if __name__ == "__main__":
    main()
