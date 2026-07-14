"""Unit tests for certs.policy (severity mapping, design doc Section 13)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from certs.models import CertificateRecord, ExpiryStatus, Rule, Severity
from certs.policy import build_findings, evaluate_certificate

NOW = datetime(2026, 7, 14, tzinfo=timezone.utc)


def _clean_record(**overrides) -> CertificateRecord:
    base = dict(
        id="cert-1",
        domain="example.com",
        subject="CN=example.com",
        issuer="CN=Root CA",
        fingerprint_sha256="a" * 64,
        fingerprint_sha1="b" * 40,
        not_before=NOW - timedelta(days=10),
        not_after=NOW + timedelta(days=300),
        expiry_status=ExpiryStatus.VALID,
        hostnames=["example.com"],
        hostname_match=True,
        chain_valid=True,
        spki_pin_match=None,
    )
    base.update(overrides)
    return CertificateRecord(**base)


def test_fully_clean_record_has_no_findings():
    assert evaluate_certificate(_clean_record()) == []


def test_expired_is_critical():
    record = _clean_record(expiry_status=ExpiryStatus.EXPIRED)
    findings = evaluate_certificate(record)
    assert len(findings) == 1
    assert findings[0].rule == Rule.EXPIRED
    assert findings[0].severity == Severity.CRITICAL


def test_expiring_soon_is_warning():
    record = _clean_record(expiry_status=ExpiryStatus.EXPIRING_SOON)
    findings = evaluate_certificate(record)
    assert len(findings) == 1
    assert findings[0].rule == Rule.EXPIRING_SOON
    assert findings[0].severity == Severity.WARNING


def test_hostname_mismatch_is_warning():
    record = _clean_record(hostname_match=False)
    findings = evaluate_certificate(record)
    assert len(findings) == 1
    assert findings[0].rule == Rule.HOSTNAME_MISMATCH
    assert findings[0].severity == Severity.WARNING


def test_chain_broken_is_critical():
    record = _clean_record(chain_valid=False)
    findings = evaluate_certificate(record)
    assert len(findings) == 1
    assert findings[0].rule == Rule.CHAIN_BROKEN
    assert findings[0].severity == Severity.CRITICAL


def test_pin_mismatch_is_critical():
    record = _clean_record(spki_pin_match=False)
    findings = evaluate_certificate(record)
    assert len(findings) == 1
    assert findings[0].rule == Rule.PIN_MISMATCH
    assert findings[0].severity == Severity.CRITICAL


def test_pin_unconfigured_produces_no_pin_finding():
    record = _clean_record(spki_pin_match=None)
    assert evaluate_certificate(record) == []


def test_multiple_findings_for_one_certificate():
    record = _clean_record(
        expiry_status=ExpiryStatus.EXPIRED,
        hostname_match=False,
        chain_valid=False,
        spki_pin_match=False,
    )
    findings = evaluate_certificate(record)
    rules = {f.rule for f in findings}
    assert rules == {Rule.EXPIRED, Rule.HOSTNAME_MISMATCH, Rule.CHAIN_BROKEN, Rule.PIN_MISMATCH}


def test_finding_carries_domain_and_certificate_id():
    record = _clean_record(id="cert-42", domain="example.com", chain_valid=False)
    finding = evaluate_certificate(record)[0]
    assert finding.certificate_id == "cert-42"
    assert finding.domain == "example.com"


def test_build_findings_aggregates_across_records():
    records = [
        _clean_record(id="a", chain_valid=False),
        _clean_record(id="b"),  # clean, contributes nothing
        _clean_record(id="c", expiry_status=ExpiryStatus.EXPIRED),
    ]
    findings = build_findings(records)
    assert {f.certificate_id for f in findings} == {"a", "c"}


@pytest.mark.parametrize("rule", list(Rule))
def test_every_rule_has_a_severity_mapping(rule):
    # Guards against adding a new Rule without wiring its severity.
    from certs.policy import _RULE_SEVERITY

    assert rule in _RULE_SEVERITY
