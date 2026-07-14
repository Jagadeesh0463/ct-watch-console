"""Orchestrates loader + parser + hostname + chain + pin into CertificateRecord
objects (Milestone 1 deliverable).

Fixture shape (domain-scoped, matching the design doc's architecture diagram
where the Certificate Loader "reads fixture files, extracts PEM blocks" and
chain linking happens "across the fixture chain"):

    {
      "domains": [
        {
          "domain": "example.com",
          "expected_spki_pins": ["<hex sha256>"],   // optional
          "certificates": [{"id": "...", "pem": "..."}, ...]
        }
      ]
    }
"""

from __future__ import annotations

from datetime import datetime

from cryptography import x509

from .chain import validate_chain
from .hostname import extract_hostnames, hostname_matches
from .loader import load_fixture_dir
from .models import CertificateRecord, ParseError
from .parser import (
    CertificateParseError,
    compute_expiry_status,
    fingerprints,
    name_to_str,
    parse_pem,
)
from .pin import pin_match


def build_certificate_records(
    fixture_dir: str,
    reference_time: datetime,
    warning_days: int = 30,
) -> tuple[list[CertificateRecord], list[ParseError]]:
    records: list[CertificateRecord] = []
    errors: list[ParseError] = []

    for domain_block in load_fixture_dir(fixture_dir):
        domain = domain_block.get("domain")
        expected_pins = domain_block.get("expected_spki_pins")
        raw_certs = domain_block.get("certificates", [])

        parsed: list[tuple[str, x509.Certificate]] = []
        for raw in raw_certs:
            fixture_id = raw.get("id") if isinstance(raw, dict) else None
            try:
                if not fixture_id:
                    raise ValueError("fixture entry is missing required 'id'")
                pem_text = raw["pem"]
                cert = parse_pem(pem_text.encode())
                parsed.append((fixture_id, cert))
            except ValueError as exc:
                errors.append(ParseError(domain=domain, fixture_id=fixture_id, reason=str(exc)))
            except CertificateParseError as exc:
                errors.append(ParseError(domain=domain, fixture_id=fixture_id, reason=str(exc)))
            except (KeyError, AttributeError, TypeError) as exc:
                errors.append(
                    ParseError(
                        domain=domain,
                        fixture_id=fixture_id,
                        reason=f"malformed fixture entry: {exc}",
                    )
                )

        pool: list[x509.Certificate] = [c for _, c in parsed]

        for cert_id, cert in parsed:
            sha256, sha1 = fingerprints(cert)
            hostnames = extract_hostnames(cert)
            not_before = cert.not_valid_before_utc
            not_after = cert.not_valid_after_utc
            records.append(
                CertificateRecord(
                    id=cert_id,
                    domain=domain,
                    subject=name_to_str(cert.subject),
                    issuer=name_to_str(cert.issuer),
                    fingerprint_sha256=sha256,
                    fingerprint_sha1=sha1,
                    not_before=not_before,
                    not_after=not_after,
                    expiry_status=compute_expiry_status(
                        not_before, not_after, reference_time, warning_days
                    ),
                    hostnames=hostnames,
                    hostname_match=hostname_matches(domain, hostnames) if domain else False,
                    chain_valid=validate_chain(cert, pool),
                    spki_pin_match=pin_match(cert, expected_pins),
                )
            )

    return records, errors
