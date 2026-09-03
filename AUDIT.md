# AUDIT — osintpy
**Date:** 2026-09-02
**Auditor:** Jim (jim-mtju7cgh)
**Repo:** [alexdrgpy06/osintpy](https://github.com/alexdrgpy06/osintpy) (public)

---

## Business thesis

OSINTpy is an OSINT (Open-Source Intelligence) aggregator for Paraguay — collects public records (RUC, padrón, news), runs username lookups across social platforms, and tracks person/business identity. Bundles four upstream OSINT tools (blackbird, holehe, sherlock, theHarvester, toutatis) into a FastAPI + Next.js dashboard. Reuses the same `@alexdrgpy06` namespace pattern.

## Tech stack

- **Backend**: FastAPI (Python), MongoDB + Neo4j + Redis, Celery worker
- **Frontend**: Next.js (`.next/` build artifacts present), Tailwind, TypeScript
- **Integrations**: blackbird (email OSINT), holehe (account lookup), sherlock (username search), theHarvester (emails/subdomains), toutatis (Instagram)
- **CI**: `.github/workflows/python-ci.yml`
- **Testing**: pytest (asyncio_mode = auto), `pytest.ini` configured
- **License**: MIT

## Repository structure

```
osintpy/
├── backend/
│   ├── main.py                  # FastAPI app
│   ├── news.py                  # news agent
│   ├── agents/                  # news, osint_tools, persistence, py_gov, feedback_processor
│   ├── ai/processor.py          # AI layer
│   ├── routes/                  # profile, search, tracking
│   ├── services/                # celery_app, identity_resolver, task_manager, health_check
│   ├── data/                    # padron_py.db, ruc_py.db (SQLite)
│   └── tests/                   # health, news, osint_tools, resolver_v10, v10_pipeline
├── frontend/                    # Next.js app
├── blackbird/                   # vendored blackbird OSINT
├── holehe/                      # vendored holehe (scaffold only)
├── sherlock/                    # vendored sherlock-project
├── theHarvester/                # vendored theharvester
├── toutatis/                    # vendored toutatis
├── .github/workflows/python-ci.yml
├── docker-compose.yml           # mongodb + neo4j + redis + backend + worker + frontend
├── benchmark.py, seed_test.py, test_direct.py, test_search.py, run_local.ps1
├── pytest.ini
└── LICENSE (MIT)
```

## Recent activity

Top commits on `main`:
- `267f1d6` Merge PR #48 — theharvester integration
- `0af0d7f` Merge PR #49 — update-dependencies
- `8e4bf1a` PR #50 — feat: ci-workflow
- `84938e5` PR #51 — cleanup-post-merge

Branches: `main` only.

## Strengths

- **Comprehensive bundling**: integrates 5+ upstream projects (blackbird, holehe, sherlock, toutatis, theHarvester).
- **Async pipeline**: Celery worker + FastAPI + MongoDB/Neo4j/Redis stack handles concurrent lookups.
- **CI workflow** present.
- **Multi-source identity**: `identity_resolver.py` (29KB) + persistence layer.
- **Public repo** with MIT license — lowers adoption friction.

## Top 3 improvement opportunities

| # | Issue | Severity | Effort | Evidence |
|---|-------|----------|--------|----------|
| 1 | **Vendored OSINT tools** (`blackbird/`, `holehe/`, `sherlock/`, `theHarvester/`, `toutatis/`) — no upstream tracking; updates require manual sync | M | M | top-level dirs |
| 2 | **`.env` checked into the repo** at `backend/.env` — credentials leak | L | S | `backend/.env:1-7` |
| 3 | **Heavy backend stack** for what's mostly a wrapper — Mongo+Neo4j+Redis for what could be SQLite + asyncio | M | L | `docker-compose.yml` (5 services) |

## Recommended next 3 actions

1. **Rotate leaked credentials** in `backend/.env` (move to `backend/.env.example` with placeholders; add `backend/.env` to `.gitignore`).
2. **Switch vendored tools to git submodules** with pinned commits — enables upstream tracking + license attribution.
3. **Simplify data layer**: profile data fits SQLite; drop Neo4j until the graph use-case is concrete (or document why it's required).

## Red flags

- **`backend/.env` committed** — real env vars likely checked in. Rotate all secrets.
- **Multiple vendored projects**: each with its own license (`blackbird/docs/LICENSE` is 35KB) — compliance review needed if redistributed.
- **5-service docker-compose** for what may be a single-user tool — operational overhead.
- **README is a single line** (`# osintpy`) — no setup docs.

## Source references

- `backend/.env:1-10`
- `docker-compose.yml:1-30`
- `.github/workflows/python-ci.yml`
- `pytest.ini:1-4`
- `LICENSE:1-5`