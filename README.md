# Certificate Transparency Watch Console

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-black)
![Tests](https://img.shields.io/badge/Tests-75_passing-success)
![Coverage](https://img.shields.io/badge/Coverage-99%25-success)
![Lint](https://img.shields.io/badge/ruff%20%7C%20black%20%7C%20mypy-clean-success)

A console that ingests CT-style certificate fixtures, normalizes each certificate into a
structured record, evaluates it against policy rules (expiry, hostname match, chain
integrity, SPKI pin), and exposes the results through a Flask API — with a React
dashboard on the way.

## Roadmap

```
████████████░░░░░░ Milestone 2 of 3

✅ Milestone 1 — Certificate parsing (PEM, fingerprints, expiry, hostname, chain, pin)
✅ Milestone 2 — Flask API + policy findings engine
⬜ Milestone 3 — React watchlist UI
```

## Status

**Milestones 1 & 2 — done.**

`backend/certs/` parses PEM certificates, computes fingerprints and SPKI hashes, checks
expiry against an injectable reference clock, matches hostnames (wildcard-aware), links
issuer/subject chains, and compares SPKI pins. `backend/certs/policy.py` turns those
normalized records into policy findings with severity (critical/warning), and
`backend/app.py` + `backend/api/routes.py` serve everything over a Flask REST API,
parsing fixtures once at startup and caching the results in memory.

For local development and testing, the project includes a deterministic fixture
generator (`backend/fixtures/generate_fixtures.py`) that produces representative
certificate scenarios — valid, expired, expiring-soon, hostname mismatch, wildcard
match, broken chain, pin mismatch, malformed entry, and self-signed-root-only chain —
until the provided assessment fixtures are available.

Milestone 3 (React watchlist UI) is not started yet.

## Features

**Milestone 1 — certificate parsing**
- Parse PEM certificates via `cryptography`
- Compute SHA-256 / SHA-1 fingerprints and SPKI SHA-256 hash
- Expiry status against an injectable reference clock (valid / expiring-soon / expired)
- Wildcard-aware hostname matching (SAN, with CN fallback)
- Issuer/subject chain linking across a fixture's certificate pool
- SPKI pin comparison, scoped to end-entity (leaf) certificates only
- Deterministic synthetic fixture generator covering all edge cases

**Milestone 2 — API + policy engine**
- Stateless policy engine mapping each certificate to zero or more findings
  (`expired`, `expiring_soon`, `hostname_mismatch`, `chain_broken`, `pin_mismatch`)
  with severity (critical / warning)
- Flask REST API: `GET /api/domains`, `/api/certificates`, `/api/certificates/<id>`,
  `/api/findings` (with `?domain=` / `?severity=` filters), `/healthz`
- Consistent `{"error": {"code", "message"}}` shape on every error response
- Environment-driven config (`FIXTURE_DIR`, `EXPIRY_WARNING_DAYS`, `REFERENCE_TIME`,
  `LOG_LEVEL`, `API_HOST`/`API_PORT`, `CORS_ORIGINS`) — no hardcoded values
- Fixtures parsed once at startup and cached in memory; load failures surface as a
  consistent 500 rather than crashing the app

**Testing**
- 75 automated tests (unit + API contract), 99% coverage across `certs/`, `api/`,
  `app.py`, `config.py`
- Clean under ruff, black, and mypy

## Repository layout

```
ct-watch-console/
├── README.md
└── backend/
    ├── app.py             # Flask application factory
    ├── config.py           # env-driven configuration
    ├── api/
    │   └── routes.py         # /api/domains, /certificates, /findings, error shapes
    ├── certs/
    │   ├── models.py          # CertificateRecord, PolicyFinding, enums
    │   ├── parser.py           # PEM parsing, fingerprints, SPKI, expiry, CA detection
    │   ├── hostname.py          # wildcard-aware SAN/CN matching
    │   ├── chain.py              # issuer/subject chain linking
    │   ├── pin.py                 # SPKI pin comparison
    │   ├── policy.py               # findings engine + severity mapping
    │   └── normalize.py             # orchestrates the above into records
    ├── fixtures/              # generate_fixtures.py + generated sample_fixtures.json
    ├── tests/                  # pytest suite (unit + API contract)
    ├── requirements.txt
    └── pyproject.toml           # pytest / ruff / black / mypy config
```

## Architecture

```
CT-style JSON fixtures
        │
        ▼
Certificate Parser   (done — Milestone 1)
        │
        ▼
Policy Engine        (done — Milestone 2)
        │
        ▼
Flask REST API        (done — Milestone 2)
        │
        ▼
React Dashboard        (Milestone 3)
```

## Backend setup

```bash
cd backend
pip install -r requirements.txt
python fixtures/generate_fixtures.py   # regenerate fixtures if needed
pytest --cov=certs --cov=api --cov=app --cov=config --cov-report=term-missing
ruff check .
black --check .
mypy certs app.py config.py api

# run the API locally
python app.py   # serves on http://0.0.0.0:5000
```

All 75 tests pass with 99% coverage across `certs/`, `api/`, `app.py`, and `config.py`.
