"""Policy findings engine (design doc Section 13: Policy Rules).

Rule -> severity mapping, verbatim from the design doc:
    expired            -> critical
    expiring_soon      -> warning
    hostname_mismatch  -> warning
    chain_broken       -> critical
    pin_mismatch       -> critical

Kept in its own module (isolated from parsing) per ADR-002/ADR-004 in the
design doc: stateless policy engine, separated from parser logic, so severity
can be adjusted in one place without touching certificate normalization.
"""

from __future__ import annotations

from .models import CertificateRecord, ExpiryStatus, PolicyFinding, Rule, Severity

_RULE_SEVERITY: dict[Rule, Severity] = {
    Rule.EXPIRED: Severity.CRITICAL,
    Rule.EXPIRING_SOON: Severity.WARNING,
    Rule.HOSTNAME_MISMATCH: Severity.WARNING,
    Rule.CHAIN_BROKEN: Severity.CRITICAL,
    Rule.PIN_MISMATCH: Severity.CRITICAL,
}


def _finding(record: CertificateRecord, rule: Rule, message: str) -> PolicyFinding:
    return PolicyFinding(
        domain=record.domain,
        certificate_id=record.id,
        rule=rule,
        severity=_RULE_SEVERITY[rule],
        message=message,
    )


def evaluate_certificate(record: CertificateRecord) -> list[PolicyFinding]:
    """Findings for a single certificate. A record can produce zero, one, or
    several findings -- e.g. an expired cert with a hostname mismatch gets two.
    """
    findings: list[PolicyFinding] = []

    if record.expiry_status == ExpiryStatus.EXPIRED:
        findings.append(
            _finding(
                record,
                Rule.EXPIRED,
                f"Certificate {record.id} expired on {record.not_after.isoformat()}",
            )
        )
    elif record.expiry_status == ExpiryStatus.EXPIRING_SOON:
        findings.append(
            _finding(
                record,
                Rule.EXPIRING_SOON,
                f"Certificate {record.id} expires on {record.not_after.isoformat()}",
            )
        )

    if not record.hostname_match:
        sans = ", ".join(record.hostnames) if record.hostnames else "none"
        findings.append(
            _finding(
                record,
                Rule.HOSTNAME_MISMATCH,
                f"Certificate {record.id} does not match watched domain "
                f"'{record.domain}' (SANs: {sans})",
            )
        )

    if not record.chain_valid:
        findings.append(
            _finding(
                record,
                Rule.CHAIN_BROKEN,
                f"Certificate {record.id}'s issuer '{record.issuer}' was not found "
                f"in the fixture chain",
            )
        )

    if record.spki_pin_match is False:
        findings.append(
            _finding(
                record,
                Rule.PIN_MISMATCH,
                f"Certificate {record.id}'s SPKI does not match the configured pin "
                f"for '{record.domain}'",
            )
        )

    return findings


def build_findings(records: list[CertificateRecord]) -> list[PolicyFinding]:
    findings: list[PolicyFinding] = []
    for record in records:
        findings.extend(evaluate_certificate(record))
    return findings
