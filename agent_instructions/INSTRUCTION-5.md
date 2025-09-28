# INSTRUCTION-5 — API Layer and Async Workers (Phase 4)
Source: [implementation_plan_2025-09-27T18-06-45Z.md](implementation_plan_2025-09-27T18-06-45Z.md)

Objective:
- Implement REST endpoints reflecting section 4.5; offload long-running runs to Celery workers; persist metadata in Postgres and artifacts in MinIO.

Principles:
- KISS: OpenAPI-first; minimal middleware; explicit contracts.
- YAGNI: defer SSO and advanced policies.

Authoritative API contracts (OpenAPI at [api/openapi.yaml](api/openapi.yaml)):
- Auth: X-API-Key required on all requests.
- [api.post_validate_import(project_id: UUID, payload: ProjectImportPayload) -> ValidationReport](api/openapi.yaml:1)
- [api.post_commit_import(project_id: UUID, payload: ProjectImportPayload) -> ProjectSnapshot](api/openapi.yaml:1)
- [api.post_runs(project_id: UUID, scenario: ScenarioConfig) -> RunEnqueued](api/openapi.yaml:1)
- [api.get_run(project_id: UUID, run_id: RunId) -> RunStatus](api/openapi.yaml:1)
- [api.get_run_results(project_id: UUID, run_id: RunId) -> RunResultsIndex](api/openapi.yaml:1)
- [reports.debrief.render_debrief(run_id: RunId, template_id: DebriefTemplateId) -> ArtifactHandle](reports/debrief_template.md:1)

Run status and artifacts:
- RunStatus: run_id; status ∈ {queued, running, completed, failed}; started_at; finished_at; progress_pct; message.
- RunResultsIndex: artifacts[] with {kind, media_type, size, url}; summary KPIs (subset).
- Storage convention: s3://{bucket}/{project_id}/{run_id}/{kind}/...

Steps:
1) Define OpenAPI endpoints and request/response schemas exactly as listed; include auth header parameter.
2) Implement async run submission to Celery worker (Redis broker); propagate request_id across API and task context.
3) Persist run metadata and status in Postgres; save artifacts in MinIO with content-hash labeling.
4) Ensure endpoints return correct contracts; implement GET endpoints for status and results; return artifact handles/URLs.

Acceptance criteria:
- Endpoints operational: POST validate/commit; POST runs; GET run; GET results; POST debriefs (handle).
- Runs execute via worker and complete; artifacts listed in RunResultsIndex.

MCP usage notes:
- Context7: FastAPI patterns for dependency injection and API key auth; Celery task signatures and progress reporting (use if connected).
- Octocode: exemplar repositories for FastAPI + Celery + MinIO patterns (use if connected).
- SequentialThinking: decisions on error handling, retries, idempotency, and request_id propagation.