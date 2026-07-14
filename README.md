# Certificate Transparency Watch Console

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Tests](https://img.shields.io/badge/Tests-38_passing-success)
![Coverage](https://img.shields.io/badge/Coverage-100%25-success)
![Lint](https://img.shields.io/badge/ruff%20%7C%20black%20%7C%20mypy-clean-success)

A console that ingests CT-style certificate fixtures, normalizes each certificate into a
structured record, evaluates it against policy rules (expiry, hostname match, chain
integrity, SPKI pin), and will expose the results through a Flask API and a React
dashboard.

## Roadmap

```
██████░░░░░░░░░░░░ Milestone 1 of 3

✅ Milestone 1 — Certificate parsing (PEM, fingerprints, expiry, hostname, chain, pin)
⬜ Milestone 2 — Flask API + policy findings engine
⬜ Milestone 3 — React watchlist UI
```

## Status

**Milestone 1 — done.**

`backend/certs/` parses PEM certificates, computes fingerprints and SPKI hashes, checks
expiry against an injectable reference clock, matches hostnames (wildcard-aware), links
issuer/subject chains, and compares SPKI pins.

For local development and testing, the project includes a deterministic fixture
generator (`backend/fixtures/generate_fixtures.py`) that produces representative
certificate scenarios — valid, expired, expiring-soon, hostname mismatch, wildcard
match, broken chain, pin mismatch, malformed entry, and self-signed-root-only chain —
until the provided assessment fixtures are available.

Milestones 2 (Flask API + policy findings) and 3 (React watchlist) are not started yet.

## Features (Milestone 1)

- Parse PEM certificates via `cryptography`
- Compute SHA-256 / SHA-1 fingerprints and SPKI SHA-256 hash
- Expiry status against an injectable reference clock (valid / expiring-soon / expired)
- Wildcard-aware hostname matching (SAN, with CN fallback)
- Issuer/subject chain linking across a fixture's certificate pool
- SPKI pin comparison
- Deterministic synthetic fixture generator covering all edge cases
- 38 automated tests, 100% coverage on `certs/`, clean under ruff/black/mypy

## Repository layout

```
ct-watch-console/
├── README.md
└── backend/
    ├── certs/            # parser, hostname, chain, pin, normalize, models
    ├── fixtures/          # generate_fixtures.py + generated sample_fixtures.json
    ├── tests/              # pytest suite (unit + integration)
    ├── requirements.txt
    └── pyproject.toml       # pytest / ruff / black / mypy config
```

## Architecture (target, end state)

```
CT-style JSON fixtures
        │
        ▼
Certificate Parser   (done — Milestone 1)
        │
        ▼
Policy Engine        (Milestone 2)
        │
        ▼
Flask REST API        (Milestone 2)
        │
        ▼
React Dashboard        (Milestone 3)
```

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
