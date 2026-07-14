"""Unit tests for certs.hostname (wildcard-aware matching)."""

from __future__ import annotations

import pytest

from certs.hostname import hostname_matches


@pytest.mark.parametrize(
    "domain, hostnames, expected",
    [
        ("example.com", ["example.com"], True),
        ("example.com", ["other.com"], False),
        ("foo.example.com", ["*.example.com"], True),
        ("example.com", ["*.example.com"], False),  # wildcard doesn't cover the bare domain
        ("a.b.example.com", ["*.example.com"], False),  # wildcard covers one label only
        ("Example.COM", ["example.com"], True),  # case-insensitive
        ("example.com", ["example.com."], True),  # trailing dot normalized
        ("foo.example.com", ["other.com", "*.example.com"], True),  # matches any SAN entry
    ],
)
def test_hostname_matches(domain, hostnames, expected):
    assert hostname_matches(domain, hostnames) is expected
