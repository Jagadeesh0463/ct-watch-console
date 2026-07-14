# Certificate Transparency Watch Console

A console that ingests CT-style certificate fixtures, normalizes each certificate into a
structured record, evaluates it against policy rules (expiry, hostname match, chain
integrity, SPKI pin), and will expose the results through a Flask API and a React
dashboard.

## Status

**Milestone 1 (certificate parsing) — done.**

`backend/certs/` parses PEM certificates, computes fingerprints and SPKI hashes, checks
expiry against an injectable reference clock, matches hostnames (wildcard-aware), links
issuer/subject chains, and compares SPKI pins. No starter fixtures were provided, so
`backend/fixtures/generate_fixtures.py` generates deterministic synthetic certificates
covering every edge case (valid, expired, expiring-soon, hostname mismatch, wildcard
match, broken chain, pin mismatch, malformed entry, self-signed-root-only chain).

Milestones 2 (Flask API + policy findings) and 3 (React watchlist) are not started yet.

## Backend setup

```bash
cd backend
pip install -r requirements.txt
python fixtures/generate_fixtures.py   # regenerate fixtures if needed
pytest --cov=certs --cov-report=term-missing
ruff check .
black --check .
mypy certs
```

All 38 tests pass with 100% coverage on `certs/`.
