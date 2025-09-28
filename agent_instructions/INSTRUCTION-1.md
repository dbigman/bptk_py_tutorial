# INSTRUCTION-1 — Project Bootstrap & Tooling (Phase 0)
Source: [implementation_plan_2025-09-27T18-06-45Z.md](implementation_plan_2025-09-27T18-06-45Z.md)

Objective:
- Establish minimal scaffolding and tooling to build and run the system locally.
- Validate linting and OpenAPI spec early.

Principles:
- KISS: only essential scaffolding and targets.
- YAGNI: defer non-essential integrations.

Preconditions:
- Python 3.11 runtime installed.
- Docker and docker-compose installed.
- Make (or Windows equivalent) available.
- Accounts/credentials: local only; use .env templates.

Discipline checkpoints (spec-workflow):
- Requirements → Design → Tasks → Implementation are used as gates for documents; do not create new spec docs in this instruction.
- Use approvals only if explicitly requested later.

Steps:
1) Create repository scaffolding paths (empty placeholders ok):
   - [schemas/](schemas/)
   - [examples/toy/](examples/toy/)
   - [engine/](engine/)
   - [kpis/](kpis/)
   - [api/](api/)
   - [ui/](ui/)
   - [reports/](reports/)
2) Prepare top-level deliverable files (placeholders, no code now):
   - [schemas/project_config.schema.json](schemas/project_config.schema.json)
   - [experiments.yaml](experiments.yaml)
   - [kpis/spec.md](kpis/spec.md)
   - [api/openapi.yaml](api/openapi.yaml)
   - [ui/Outline.md](ui/Outline.md)
   - [reports/debrief_template.md](reports/debrief_template.md)
   - [Makefile](Makefile)
3) Docker-compose (services only - no code detail):
   - Services: fastapi, worker (Celery), redis, postgres, minio
   - Networking: single bridge network; healthchecks
   - Volumes: bind mounts for code, named volumes for data
   - Environment: local .env loaded by compose
4) .env templates:
   - CORE: APP_ENV=local, X_API_KEY, POSTGRES_URL, REDIS_URL, MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET
   - Store in .env.example; copy to .env for local use
5) CI/Lint:
   - Configure lint target to run type checks + style checks
   - Add OpenAPI validation: swagger-cli validate [api/openapi.yaml](api/openapi.yaml)
6) Observability baseline:
   - Structured logs: request_id, run_id, project_id, scenario_id, seed, phase, duration_ms, outcome
   - Metrics to emit: runs_queued, runs_started, runs_completed, run_duration_seconds, failures_count

Authoritative interfaces (no code in this phase):
- API auth: header X-API-Key on all endpoints (see [api/openapi.yaml](api/openapi.yaml))
- Storage convention: s3://{bucket}/{project_id}/{run_id}/{kind}/...

Acceptance criteria:
- docker compose up builds all services locally and shows healthy containers
- make lint passes; swagger-cli validate passes

MCP usage notes:
- Context7: consult FastAPI and Celery contract patterns; validate OpenAPI snippets (if connected)
- SequentialThinking: record design decision logs and assumptions
- Octocode: search exemplars for project structure and OpenAPI patterns when ambiguous