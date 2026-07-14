# Certificate Transparency Watch Console

![CI](https://github.com/Jagadeesh0463/ct-watch-console/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-black)
![React](https://img.shields.io/badge/React-18-61DAFB)
![Backend Tests](https://img.shields.io/badge/Backend_tests-75_passing-success)
![Coverage](https://img.shields.io/badge/Coverage-99%25-success)
![Lint](https://img.shields.io/badge/ruff%20%7C%20black%20%7C%20mypy-clean-success)
![Docker](https://img.shields.io/badge/Docker%20Compose-ready-2496ED)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A console that ingests CT-style certificate fixtures, normalizes each certificate into a
structured record, evaluates it against policy rules (expiry, hostname match, chain
integrity, SPKI pin), and exposes the results through a Flask API and a React dashboard.

## Roadmap

```
██████████████████ Milestone 3 of 3

✅ Milestone 1 — Certificate parsing (PEM, fingerprints, expiry, hostname, chain, pin)
✅ Milestone 2 — Flask API + policy findings engine
✅ Milestone 3 — React watchlist UI + Docker Compose
```

## Status

**All three milestones implemented.**

`backend/certs/` parses PEM certificates, computes fingerprints and SPKI hashes, checks
expiry against an injectable reference clock, matches hostnames (wildcard-aware), links
issuer/subject chains, and compares SPKI pins. `backend/certs/policy.py` turns those
normalized records into policy findings with severity (critical/warning), and
`backend/app.py` + `backend/api/routes.py` serve everything over a Flask REST API,
parsing fixtures once at startup and caching the results in memory. `frontend/` is a
Vite + React dashboard styled with Tailwind CSS and lucide-react icons (summary stat
cards, a domain watchlist with search/severity filters, a critical findings banner,
and a grouped certificate detail view with copy-to-clipboard fingerprints) that talks
to that API. `docker-compose.yml` brings both services up with one command.

For local development and testing, the project includes a deterministic fixture
generator (`backend/fixtures/generate_fixtures.py`) that produces representative
certificate scenarios — valid, expired, expiring-soon, hostname mismatch, wildcard
match, broken chain, pin mismatch, malformed entry, and self-signed-root-only chain —
until the provided assessment fixtures are available.

**Note on the Playwright suite:** `frontend/e2e/watchlist.spec.ts` covers all three
Milestone 3 UI acceptance criteria (domain filter narrows the list, critical findings
are visually highlighted, the detail view shows correct certificate fields) and is
wired into `playwright.config.ts` to boot both the Flask backend and the built frontend
automatically. It runs on every push via `.github/workflows/ci.yml` — see the CI badge
above, or the [Actions tab](https://github.com/Jagadeesh0463/ct-watch-console/actions)
for the current run. It was developed in a sandboxed environment without `sudo` access
to install Chromium's system dependencies, so it could only be verified by hand against
the live API and DOM there; CI (a full Ubuntu runner) is what actually executes it in a
real browser. To run it yourself: `npx playwright install --with-deps` once, then
`npm run test:e2e`.

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

**Milestone 3 — React dashboard + Docker**
- Dark, Tailwind CSS-styled dashboard with summary stat cards (total domains,
  critical / warning / healthy counts) and lucide-react icons throughout
- Domain watchlist with live search and a severity filter (critical / warning / healthy)
- Collapsible findings banner highlighting critical issues, with an explicit "all clear" state
- Certificate detail view grouped into Certificate / Validity / Security Checks /
  Fingerprints sections, switchable across every certificate in a domain's chain
  (leaf / intermediate / root), with copy-to-clipboard on fingerprint hashes
- `docker-compose.yml`: two services (`backend`, `frontend`), fixtures mounted
  read-only, backend healthcheck via `/healthz`, all config via environment variables

**Testing**
- 75 backend tests (unit + API contract), 99% coverage across `certs/`, `api/`,
  `app.py`, `config.py`, clean under ruff/black/mypy
- Playwright e2e suite written for all 3 UI acceptance criteria (not yet run — see note above)

## Repository layout

```
ct-watch-console/
├── README.md
├── docker-compose.yml
├── docker/
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
├── backend/
│   ├── app.py             # Flask application factory
│   ├── config.py           # env-driven configuration
│   ├── api/
│   │   └── routes.py         # /api/domains, /certificates, /findings, error shapes
│   ├── certs/
│   │   ├── models.py          # CertificateRecord, PolicyFinding, enums
│   │   ├── parser.py           # PEM parsing, fingerprints, SPKI, expiry, CA detection
│   │   ├── hostname.py          # wildcard-aware SAN/CN matching
│   │   ├── chain.py              # issuer/subject chain linking
│   │   ├── pin.py                 # SPKI pin comparison
│   │   ├── policy.py               # findings engine + severity mapping
│   │   └── normalize.py             # orchestrates the above into records
│   ├── fixtures/              # generate_fixtures.py + generated sample_fixtures.json
│   ├── tests/                  # pytest suite (unit + API contract)
│   ├── requirements.txt         # runtime deps only
│   ├── requirements-dev.txt      # + pytest/ruff/black/mypy
│   └── pyproject.toml             # pytest / ruff / black / mypy config
└── frontend/
    ├── src/
    │   ├── App.jsx              # top-level layout + data fetching
    │   ├── api.js                 # Flask API client
    │   ├── index.css               # Tailwind entrypoint + base styles
    │   └── components/
    │       ├── StatCard.jsx          # summary KPI cards (domains/critical/warning/healthy)
    │       ├── DomainList.jsx         # search + severity filter
    │       ├── FindingsBanner.jsx      # critical findings highlight
    │       └── CertificateDetail.jsx    # grouped per-certificate field view
    ├── tailwind.config.js       # dark theme color tokens
    ├── postcss.config.js
    ├── e2e/watchlist.spec.ts      # Playwright
    └── playwright.config.ts
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
React Dashboard        (done — Milestone 3)
```

## Run everything with Docker Compose

```bash
docker compose up --build
```

Backend: http://localhost:5000 · Frontend: http://localhost:8080

## Backend setup (without Docker)

```bash
cd backend
pip install -r requirements-dev.txt
python fixtures/generate_fixtures.py   # regenerate fixtures if needed
pytest --cov=certs --cov=api --cov=app --cov=config --cov-report=term-missing
ruff check .
black --check .
mypy certs app.py config.py api

python app.py   # serves on http://0.0.0.0:5000
```

All 75 tests pass with 99% coverage across `certs/`, `api/`, `app.py`, and `config.py`.

## Frontend setup (without Docker)

```bash
cd frontend
npm install
npm run dev       # http://localhost:5173, talks to the backend on :5000
npm run build     # production build to dist/

# e2e (requires the backend's dependencies installed too, and a one-time
# `npx playwright install --with-deps` on a machine that allows it):
npm run test:e2e
```

## CI

`.github/workflows/ci.yml` runs on every push and pull request to `main`: backend
lint/type-check/tests (ruff, black, mypy, pytest), a frontend production build, and the
full Playwright suite against a real Chromium browser. See the CI badge at the top of
this file or the [Actions tab](https://github.com/Jagadeesh0463/ct-watch-console/actions).

## License

[MIT](LICENSE)
