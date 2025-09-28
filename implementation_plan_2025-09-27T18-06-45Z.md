# Implementation Plan — HMLV Manufacturing Simulator MVP (Profile A)

Plan timestamp (UTC): 2025-09-27T18:06:45Z
Target file: [implementation_plan_2025-09-27T18-06-45Z.md](implementation_plan_2025-09-27T18-06-45Z.md)

1. Scope alignment
- Aligns to TASK_HMLV_Simulator_MVP.md and hmlv_manufacturing_simulator_prd_v_0.md.
- MVP goals: data import; baseline vs scenario runs (EDD, SPT, ATC/ATCS, LSN; CONWIP/POLCA; failures/PM; rework); KPIs; one-page debrief; OpenAPI; React UI outline.
- Out of scope: 3D/layout, ERP connectors, SSO (deferred), advanced PM.

2. Reference architecture (Profile A)
- Language/runtime: Python 3.11
- Simulation core: BPTK-Py hybrid (ABM + SD) with deterministic seeds
- API: FastAPI (REST, OpenAPI-first)
- Async runs: Celery + Redis broker (parallel scenarios)
- Storage: PostgreSQL 15 (metadata), MinIO/S3 (artifacts: CSVs, JSON, PDF)
- Frontend: Next.js 14 (React) consuming REST endpoints
- Reporting: Markdown to PDF (WeasyPrint); CSV exports
- Auth (MVP): X-API-Key header on all endpoints
- Packaging/Dev: Docker + docker-compose; Makefile targets

3. Deliverables index (files to be created by phases)
- [schemas/project_config.schema.json](schemas/project_config.schema.json)
- [examples/toy/products.csv](examples/toy/products.csv)
- [examples/toy/routings.csv](examples/toy/routings.csv)
- [examples/toy/machines.csv](examples/toy/machines.csv)
- [examples/toy/operators.csv](examples/toy/operators.csv)
- [examples/toy/setup_matrix.csv](examples/toy/setup_matrix.csv)
- [examples/toy/demand.csv](examples/toy/demand.csv)
- [examples/toy/calendars.csv](examples/toy/calendars.csv)
- [examples/toy/mtbf_mttr.csv](examples/toy/mtbf_mttr.csv)
- [examples/toy/yields.csv](examples/toy/yields.csv)
- [examples/toy/skills.csv](examples/toy/skills.csv)
- [engine/__init__.py](engine/__init__.py)
- [engine/agents.py](engine/agents.py)
- [engine/dispatch.py](engine/dispatch.py)
- [engine/failures.py](engine/failures.py)
- [engine/rework.py](engine/rework.py)
- [engine/release_control.py](engine/release_control.py)
- [engine/run.py](engine/run.py)
- [experiments.yaml](experiments.yaml)
- [kpis/spec.md](kpis/spec.md)
- [kpis/compute.py](kpis/compute.py)
- [api/openapi.yaml](api/openapi.yaml)
- [ui/Outline.md](ui/Outline.md)
- [reports/debrief_template.md](reports/debrief_template.md)
- [Makefile](Makefile)

4. Contracts catalog (authoritative interfaces, zero implementation detail)

4.1 Data contracts
- Project import JSON Schema: [schemas/project_config.schema.json](schemas/project_config.schema.json)
  - Top-level keys: plant, products[], routings[], machines[], operators[], setup_matrix[], demand[], calendars[], mtbf_mttr[], yields[], skills[].
  - Constraints: referential integrity across arrays; numeric constraints (e.g., process_time_mean > 0, setup_time ≥ 0); enums for dispatch rules; timezones IANA.
- CSV template headers: in examples/toy/*.csv (one authoritative header row each).
- Experiment configuration document: [experiments.yaml](experiments.yaml) defining scenario parameters and sweeps.

4.2 Engine module contracts (callable interfaces)
- [engine.run.create_run_manifest(project_id: UUID, scenario: ScenarioConfig, seed: int) -> RunManifest](engine/run.py:12)
- [engine.run.run_simulation(manifest: RunManifest) -> RunResultHandle](engine/run.py:20)
- [engine.run.collect_artifacts(handle: RunResultHandle) -> ArtifactIndex](engine/run.py:28)
- [engine.dispatch.select_next_job(queue_state: QueueState, rule: DispatchRule, now: Time) -> JobId](engine/dispatch.py:12)
- [engine.dispatch.compute_priority(rule: DispatchRule, job: JobView, state: QueueState, now: Time) -> float](engine/dispatch.py:22)
- [engine.release_control.release_jobs(now: Time, policy: ReleasePolicy, state: SystemState) -> list[JobId]](engine/release_control.py:12)
- [engine.release_control.token_balance(route: RouteId) -> int](engine/release_control.py:20)
- [engine.failures.next_downtime(machine_id: MachineId, now: Time) -> DowntimeWindow](engine/failures.py:12)
- [engine.rework.apply_rework_if_needed(job: JobId, step: RouteStep, outcome: InspectionOutcome) -> Optional[RouteStep]](engine/rework.py:12)
- [engine.agents.get_machine_view(machine_id: MachineId) -> MachineView](engine/agents.py:12)
- [engine.agents.update_operator_allocation(now: Time) -> None](engine/agents.py:20)

4.3 KPI and reporting contracts
- [kpis.compute.compute_kpis(run_id: RunId) -> KPIReport](kpis/compute.py:12)
- [kpis.compute.export_kpis_csv(report: KPIReport, destination: ArtifactPath) -> ArtifactHandle](kpis/compute.py:22)
- [reports.debrief.render_debrief(run_id: RunId, template_id: DebriefTemplateId) -> ArtifactHandle](reports/debrief_template.md:1)

4.4 Experiment runner contracts
- [engine.run.generate_scenarios(base: ScenarioSpec, sweeps: ParamSweepSpec) -> list[ScenarioConfig]](engine/run.py:36)
- [engine.run.execute_experiments(configs: list[ScenarioConfig], seed_base: int, parallelism: int) -> ExperimentBatchId](engine/run.py:44)
- [engine.run.get_experiment_batch(batch_id: ExperimentBatchId) -> ExperimentBatchView](engine/run.py:52)

4.5 API contracts (endpoint semantics; OpenAPI resides at [api/openapi.yaml](api/openapi.yaml))
- Auth: header X-API-Key: string required on all requests
- POST /projects/{id}/import:validate → 200 ValidationReport; 400 on schema errors
- POST /projects/{id}/import:commit → 201 ProjectSnapshot with snapshot_id
- POST /projects/{id}/runs → 202 Run enqueued with run_id
- GET /projects/{id}/runs/{run_id} → 200 RunStatus
- GET /projects/{id}/runs/{run_id}/results → 200 RunResultsIndex (artifact links)
- POST /projects/{id}/debriefs → 201 DebriefArtifact handle

4.6 Storage contracts
- Artifact store paths by convention: s3://{bucket}/{project_id}/{run_id}/{kind}/...
- [engine.run.store_artifact(run_id: RunId, kind: ArtifactKind, payload: Bytes, media_type: str) -> ArtifactHandle](engine/run.py:60)
- [engine.run.load_artifact(handle: ArtifactHandle) -> Bytes](engine/run.py:68)

4.7 Observability contracts
- Structured logs include: request_id, run_id, project_id, scenario_id, seed, phase, duration_ms, outcome
- Metrics emitted: runs_queued, runs_started, runs_completed, run_duration_seconds, failures_count

5. Phased implementation plan

Phase 0 — Project bootstrap (1–2 days)
- Initialize repo scaffolding; add Makefile targets: run_toy, lint, debrief, test
- Docker-compose for API, worker, Redis, Postgres, MinIO; environment .env templates
- CI linting gates and swagger-cli validation for [api/openapi.yaml](api/openapi.yaml)
Success criteria:
- docker compose up builds all services locally
- make lint passes; swagger-cli validate passes; containers healthy

Phase 1 — Data contract pack (3–4 days)
- Author [schemas/project_config.schema.json](schemas/project_config.schema.json) with cross-file references and constraints
- Prepare toy dataset in [examples/toy/*](examples/toy/)
- Define validation pipeline producing ValidationReport
Contracts to honor:
- [engine.run.validate_project_config(doc: JSON) -> ValidationReport](engine/run.py:76)
- [engine.run.map_csvs_to_project(documents: list[CSV]) -> ProjectConfig](engine/run.py:84)
Success criteria:
- All toy CSVs validate; one negative test fails with helpful diagnostics
- Example ValidationReport includes warnings/errors with row/column references

Phase 2 — Engine scaffolding (ABM + SD wrapper) (5–7 days)
- Implement actor/queue abstractions; plug dispatch rules; apply setup matrix; handle failures and simple PM windows; rework loops; release control via tokens
- Deterministic seeds and run manifest pattern
Contracts to honor:
- [engine.run.create_run_manifest(project_id: UUID, scenario: ScenarioConfig, seed: int) -> RunManifest](engine/run.py:12)
- [engine.dispatch.select_next_job(queue_state: QueueState, rule: DispatchRule, now: Time) -> JobId](engine/dispatch.py:12)
- [engine.release_control.release_jobs(now: Time, policy: ReleasePolicy, state: SystemState) -> list[JobId]](engine/release_control.py:12)
- [engine.failures.next_downtime(machine_id: MachineId, now: Time) -> DowntimeWindow](engine/failures.py:12)
- [engine.rework.apply_rework_if_needed(job: JobId, step: RouteStep, outcome: InspectionOutcome) -> Optional[RouteStep]](engine/rework.py:12)
Success criteria:
- Toy baseline run executes and produces queue timeline data and simple CSV artifacts
- Seeded re-run reproduces identical KPIs within tolerance

Phase 3 — Experiment runner (2–3 days)
- Support sweeps via [experiments.yaml](experiments.yaml) with parameters for setup_time_factor, wip_cards, rule, add_floater, etc.
- Batch run orchestration with unique seeds and parallelism
Contracts to honor:
- [engine.run.generate_scenarios(base: ScenarioSpec, sweeps: ParamSweepSpec) -> list[ScenarioConfig]](engine/run.py:36)
- [engine.run.execute_experiments(configs: list[ScenarioConfig], seed_base: int, parallelism: int) -> ExperimentBatchId](engine/run.py:44)
Success criteria:
- N (≥10) scenarios run in parallel locally; batch result index persisted; per-scenario seed logged

Phase 4 — API layer and async workers (3–4 days)
- FastAPI endpoints reflecting section 4.5; Celery tasks for long-running runs; persist metadata in Postgres; save artifacts in MinIO
- Authentication via X-API-Key middleware; request_id propagation
Contracts to honor:
- [api.post_validate_import(project_id: UUID, payload: ProjectImportPayload) -> ValidationReport](api/openapi.yaml:1)
- [api.post_commit_import(project_id: UUID, payload: ProjectImportPayload) -> ProjectSnapshot](api/openapi.yaml:1)
- [api.post_runs(project_id: UUID, scenario: ScenarioConfig) -> RunEnqueued](api/openapi.yaml:1)
- [api.get_run(project_id: UUID, run_id: RunId) -> RunStatus](api/openapi.yaml:1)
- [api.get_run_results(project_id: UUID, run_id: RunId) -> RunResultsIndex](api/openapi.yaml:1)
Success criteria:
- Endpoints return correct contracts; runs execute via worker and complete; artifacts listed

Phase 5 — KPI computation and reporting (2–3 days)
- Author [kpis/spec.md](kpis/spec.md) with definitions for OTD %, lead time avg/p90, WIP, utilization, setup hours, scrap/rework; include sampling windows and units
- Implement KPI aggregation and CSV export; debrief Markdown template with placeholders in [reports/debrief_template.md](reports/debrief_template.md)
Contracts to honor:
- [kpis.compute.compute_kpis(run_id: RunId) -> KPIReport](kpis/compute.py:12)
- [kpis.compute.export_kpis_csv(report: KPIReport, destination: ArtifactPath) -> ArtifactHandle](kpis/compute.py:22)
- [reports.debrief.render_debrief(run_id: RunId, template_id: DebriefTemplateId) -> ArtifactHandle](reports/debrief_template.md:1)
Success criteria:
- KPIs printed as compact table and written to CSV; debrief renders to PDF via pipeline

Phase 6 — UI contracts and outline (2–3 days)
- Create [ui/Outline.md](ui/Outline.md) with component responsibilities and API interactions for Data Wizard, Scenario Table, Results Dashboard, Debrief view
- Define navigation, state shape, and data fetching contracts
Contracts (UI to API):
- Data Wizard uses POST validate/commit; shows per-file validation; uploads via multipart/form-data
- Scenario Table uses POST runs; displays seeds and parameters; links to run status
- Results Dashboard calls GET run, GET results; displays delta vs baseline
- Debrief View calls POST debriefs and streams PDF
Success criteria:
- Outline accepted; mock flows traced end-to-end with sample responses

Phase 7 — Validation playbook (1–2 days)
- Document calibration steps against last 30–90 days; acceptance criterion ±10% error on OTD/lead time
- Add runbooks for importing samples and reproducing baseline vs two scenarios
Deliverables:
- Validation/README.md with checklist and sign-off rubric
Success criteria:
- Calibration on toy dataset passes; steps are unambiguous and repeatable

Phase 8 — Non-functional hardening (ongoing, 2–3 days buffer)
- Performance: target 10k jobs ≤5 minutes on standard VM; parallel experiments
- Reliability: deterministic replays; idempotent import; retries on tasks
- Security: API key rotation; secrets via env; audit logging minimal PII
- Accessibility: basic UI outline follows WCAG 2.1 AA considerations
Success criteria:
- Load test of toy scale passes; resilience verified via worker restart test

6. Detailed endpoint contracts (request/response shapes)

POST /projects/{id}/import:validate
- Request: headers X-API-Key; body ProjectImportPayload (JSON with all CSVs embedded as arrays or multipart with files)
- Response 200 ValidationReport: valid: bool; warnings[]; errors[] (each with file, row, column, message)
- Errors: 400 schema violation; 401 unauthorized

POST /projects/{id}/import:commit
- Request: same payload; optional commit_note
- Response 201 ProjectSnapshot: snapshot_id; project_id; imported_at; file_counts; checksum
- Errors: 400 invalid or not previously validated; 401 unauthorized

POST /projects/{id}/runs
- Request: ScenarioConfig including dispatch_rule, wip_caps, calendars, toggles; optional seed
- Response 202 RunEnqueued: run_id; project_id; status=queued; seed
- Errors: 400 invalid config; 401 unauthorized; 409 project not ready

GET /projects/{id}/runs/{run_id}
- Response 200 RunStatus: run_id; status ∈ {queued, running, completed, failed}; started_at; finished_at; progress_pct; message
- Errors: 404 not found; 401 unauthorized

GET /projects/{id}/runs/{run_id}/results
- Response 200 RunResultsIndex: artifacts[] with {kind, media_type, size, url}; summary KPIs (subset)
- Errors: 404 not ready; 401 unauthorized

POST /projects/{id}/debriefs
- Request: run_id; template_id (default)
- Response 201 DebriefArtifact: artifact_handle; url; expires_at
- Errors: 404 run not complete; 401 unauthorized

7. KPI definitions (spec pointers)
- OTD %: on-time delivery percent; threshold = due_date ≥ completion_time; sampling: all jobs
- Lead time avg/p90: completion_time − release_time; sampling: all jobs; p90 as percentile
- WIP: time-averaged job count in system; units: jobs
- Machine/labor utilization: busy_time / available_time; units: %
- Setup hours: sum of setup_time across machines; units: hours
- Scrap/rework rate: rework_count / inspected_count; units: %
Full formulas enumerated in [kpis/spec.md](kpis/spec.md)

8. Data model inventories (selected fields)
- products.csv: product_id, family_id, name
- routings.csv: product_id, step_number, machine_group_id, process_time_mean, process_time_sd
- machines.csv: machine_id, cell_id, name, capacity
- operators.csv: operator_id, skills[], shift_calendar_id
- setup_matrix.csv: from_family_id, to_family_id, setup_time
- demand.csv: product_id, due_date, quantity, release_policy_tags
- calendars.csv: calendar_id, timezone, blackout_windows[]
- mtbf_mttr.csv: machine_id, mtbf_hours, mttr_hours
- yields.csv: step_id, yield_rate, rework_probability
- skills.csv: operator_id, machine_group_id, level

9. Acceptance gates per phase (exit criteria)
- 0: Compose up healthy; lint and spec validations pass
- 1: Toy CSVs validate; negative case produces actionable errors
- 2: Baseline run produces stable artifacts and timeline CSVs
- 3: ≥10 scenarios executed in parallel with unique seeds
- 4: Endpoints operational with persisted runs and artifacts
- 5: KPIs computed and exported; debrief generated
- 6: UI outline reviewed; user flows mapped to API calls
- 7: Calibration doc approved; ±10% error target documented
- 8: Performance and resilience checks pass

10. Operational runbook excerpts (commands to implement later)
- Makefile targets: run_toy, lint, debrief, test, compose_up, compose_down
- Environments: local docker-compose; seeds and versions pinned
- Observability: logs tagged by request_id and run_id; artifacts labeled with content-hash

11. Risks and mitigations
- Data quality variability → strong ValidationReport and field-level errors
- Long-running simulations → Celery with timeouts and progress updates
- Non-determinism from randomness → seed management and manifest-logged RNG state
- Scope creep in UI → restrict to outline; implement endpoints first

12. Timeline (conservative, person-days)
- Phase 0: 2; Phase 1: 4; Phase 2: 7; Phase 3: 3; Phase 4: 4; Phase 5: 3; Phase 6: 3; Phase 7: 2; Phase 8: 3
- Total: ~31 person-days; parallelization possible for Phases 1/2/4/5

13. Dependency matrix
- Phase 2 depends on Phase 1 schema/contracts
- Phase 3 depends on Phase 2 run manifest
- Phase 4 depends on Phase 2 run callable and storage contracts
- Phase 5 depends on artifacts produced by Phase 2/4
- Phase 6 depends on stable API contracts in Phase 4
- Phase 7 depends on all artifacts and KPI readiness

14. Appendix — Contract data types (nomenclature)
- UUID: RFC 4122 string
- Time: ISO 8601 instant (UTC)
- ArtifactHandle: opaque string resolving to S3 URL
- RunStatus: queued | running | completed | failed
- DispatchRule: EDD | SPT | ATC | ATCS | LSN
- ReleasePolicy: CONWIP | POLCA

15. MCP and documentation workflow notes
- Use Context7 to retrieve current FastAPI and Celery contract patterns and validate OpenAPI snippets before commit
- Use SequentialThinking for design decision logs across phases; attach reasoning to PRs
- Use Octocode to search exemplars for project structure and OpenAPI patterns when ambiguous

End of plan.