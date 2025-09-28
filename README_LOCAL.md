HMLV Manufacturing Simulator — Local Bootstrap & Quickstart

This file describes the minimal steps to run the Phase‑0 bootstrap locally (scaffolding, API skeleton, and example data). Use these steps when developing or verifying the repository on your machine.

Prerequisites
- Docker & docker-compose (or Docker Desktop)
- Node/npm (for swagger-cli if validating OpenAPI locally)
- Python 3.11 (for running local checks)
- Optional: Make on non-Windows systems (Makefile targets shown)

Key files created in this phase (quick refs)
- API server entry: [`api/main.py`](api/main.py:1)
- OpenAPI spec (skeleton): [`api/openapi.yaml`](api/openapi.yaml:1)
- Docker container definition: [`Dockerfile`](Dockerfile:1)
- Compose to launch services: [`docker-compose.yml`](docker-compose.yml:1)
- Make targets (lint, compose_up, run_toy): [`Makefile`](Makefile:1)
- Environment template: [`.env.example`](.env.example:1)
- Engine stubs: [`engine/run.py`](engine/run.py:1), [`engine/agents.py`](engine/agents.py:1), [`engine/dispatch.py`](engine/dispatch.py:1), [`engine/release_control.py`](engine/release_control.py:1)
- Examples (toy CSVs): [`examples/toy/`](examples/toy/:1)
- CI pipeline skeleton: [`.github/workflows/ci.yml`](.github/workflows/ci.yml:1)

1) Quick local validation (recommended)
- Copy environment and adjust as needed:
  - Windows (PowerShell): copy .env.example .env
  - Unix: cp .env.example .env
- Validate OpenAPI (optional, requires swagger-cli):
  - npm i -g @apidevtools/swagger-cli
  - swagger-cli validate api/openapi.yaml
  - See [`api/openapi.yaml`](api/openapi.yaml:1)

2) Run services with Docker (recommended)
- Build and start containers (API will run via Uvicorn):
  - docker-compose up --build
  - Compose is defined in [`docker-compose.yml`](docker-compose.yml:1) and the API image is built from [`Dockerfile`](Dockerfile:1)
- Health:
  - API health endpoint: GET http://localhost:8000/health
  - MinIO console: http://localhost:9001
  - Postgres: port 5432, Redis: 6379

3) Development & linting
- Lint / typecheck (locally):
  - python -m mypy api engine
  - flake8 api engine
  - Or use the Makefile (if you have make available):
    - make lint
- CI (runs on push) uses [`.github/workflows/ci.yml`](.github/workflows/ci.yml:1)

4) Running a quick toy run (Phase 0 placeholder)
- The `run_toy` Makefile target calls `python -m main` which is a placeholder.
- The API endpoints exist and return phase‑0 stub responses:
  - POST /projects/{project_id}/import:validate → ValidationReport
  - POST /projects/{project_id}/import:commit → ProjectSnapshot
  - POST /projects/{project_id}/runs → RunEnqueued
  - GET /projects/{project_id}/runs/{run_id} → RunStatus
  - GET /projects/{project_id}/runs/{run_id}/results → RunResultsIndex
  - POST /projects/{project_id}/debriefs → DebriefArtifact
  - See the OpenAPI skeleton at [`api/openapi.yaml`](api/openapi.yaml:1)

5) Next recommended steps (developer guidance)
- Implement Phase 2 engine behaviors (actor/queue abstractions, dispatch rules, failures, rework) in:
  - [`engine/run.py`](engine/run.py:1)
  - [`engine/dispatch.py`](engine/dispatch.py:1)
  - [`engine/failures.py`](engine/failures.py:1)
- Implement KPI computation in [`kpis/`](kpis/:1)
- Wire artifacts to MinIO and metadata to Postgres (Phase 4)
- Add tests and a small integration that runs `docker-compose up` then exercises the API

Notes
- The codebase contains example and tutorial folders which are excluded from mypy checks for the Phase 0 bootstrap to avoid duplicate-module noise.
- All Phase 0 engine functions are intentionally minimal and deterministic to allow iteration and CI validation without heavy dependencies.

If you want, I will:
- Start the API in Docker and verify the /health endpoint (requires Docker available here), or
- Implement KPI CSV export in [`kpis/compute.py`](kpis/compute.py:1), or
- Continue with wiring Celery worker tasks and verifying enqueue/run flows.

Pick one next action and I will proceed.