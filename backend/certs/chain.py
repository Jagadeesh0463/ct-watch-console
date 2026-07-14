"""Issuer/subject chain linking within a domain's fixture cert pool.

Per the design doc (Section 13): "chain_broken -- issuer DN has no matching
subject DN in fixture chain". This is intentionally a DN-string match, not a
cryptographic signature check -- that is the literal rule as specified. One
consequence (also literal, not a special case we added): a self-signed root's
issuer DN equals its own subject DN, so it satisfies the check against a pool
that includes itself, meaning a root-only chain validates cleanly.
"""

from __future__ import annotations

from cryptography import x509

from .parser import name_to_str


def validate_chain(cert: x509.Certificate, pool: list[x509.Certificate]) -> bool:
    issuer_dn = name_to_str(cert.issuer)
    subject_dns = {name_to_str(c.subject) for c in pool}
    return issuer_dn in subject_dns
