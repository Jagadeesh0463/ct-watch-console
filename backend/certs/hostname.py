"""SAN/CN extraction and wildcard-aware hostname matching (Milestone 1)."""

from __future__ import annotations

from cryptography import x509
from cryptography.x509.oid import ExtensionOID, NameOID


def extract_hostnames(cert: x509.Certificate) -> list[str]:
    """SAN dNSName entries if present, else fall back to the CN (design doc
    Section 15: "Missing SAN extension -> Fall back to CN only")."""
    try:
        ext = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
        san = ext.value
        if isinstance(san, x509.SubjectAlternativeName):
            names = san.get_values_for_type(x509.DNSName)
            if names:
                return list(names)
    except x509.ExtensionNotFound:
        pass
    return [str(attr.value) for attr in cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)]


def _matches_one(pattern: str, hostname: str) -> bool:
    pattern = pattern.lower().rstrip(".")
    hostname = hostname.lower().rstrip(".")
    if pattern == hostname:
        return True
    if pattern.startswith("*."):
        suffix = pattern[1:]  # e.g. ".example.com"
        if not hostname.endswith(suffix):
            return False
        remaining = hostname[: -len(suffix)]
        # RFC 6125-style: wildcard covers exactly one non-empty left-most label
        return bool(remaining) and "." not in remaining
    return False


def hostname_matches(domain: str, hostnames: list[str]) -> bool:
    return any(_matches_one(h, domain) for h in hostnames)
