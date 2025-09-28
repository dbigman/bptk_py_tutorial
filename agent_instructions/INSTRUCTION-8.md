# INSTRUCTION-8 — Validation Playbook & Non-Functional Hardening (Phases 7–8)
Source: [implementation_plan_2025-09-27T18-06-45Z.md](implementation_plan_2025-09-27T18-06-45Z.md)

Objective:
- Document calibration process and runbooks; harden performance, reliability, security, and accessibility.

Principles:
- KISS: concise checklists; measurable targets.
- YAGNI: avoid premature optimization beyond stated targets.

Deliverables:
- Validation/README.md with checklist and sign-off rubric.

Calibration steps:
- Use last 30–90 days of data.
- Acceptance criterion: ±10% error on OTD and lead time against ground truth.
- Add runbooks for importing samples and reproducing baseline vs two scenarios.

Non-functional hardening targets:
- Performance: target 10k jobs ≤ 5 minutes on standard VM; parallel experiments via worker.
- Reliability: deterministic replays; idempotent import; retries on tasks; resilience verified via worker restart test.
- Security: API key rotation; secrets via env; audit logging with minimal PII.
- Accessibility: UI outline follows WCAG 2.1 AA considerations.

Observability contracts:
- Structured logs include: request_id, run_id, project_id, scenario_id, seed, phase, duration_ms, outcome.
- Metrics: runs_queued, runs_started, runs_completed, run_duration_seconds, failures_count.

Authoritative interfaces and storage conventions:
- Storage: s3://{bucket}/{project_id}/{run_id}/{kind}/...
- [engine.run.store_artifact(run_id: RunId, kind: ArtifactKind, payload: Bytes, media_type: str) -> ArtifactHandle](engine/run.py:60)
- [engine.run.load_artifact(handle: ArtifactHandle) -> Bytes](engine/run.py:68)
- [api.get_run(project_id: UUID, run_id: RunId) -> RunStatus](api/openapi.yaml:1)
- [api.get_run_results(project_id: UUID, run_id: RunId) -> RunResultsIndex](api/openapi.yaml:1)
- [reports.debrief.render_debrief(run_id: RunId, template_id: DebriefTemplateId) -> ArtifactHandle](reports/debrief_template.md:1)

Steps:
1) Write Validation/README.md including:
   - Calibration dataset sourcing and time window (30–90 days).
   - Procedure for importing samples and running baseline vs two scenarios.
   - KPIs to compare (OTD %, lead time avg/p90) and target tolerances (±10%).
   - Sign-off rubric (who approves, what evidence required).
2) Define load-test procedure targeting toy scale; include seed management and reproducibility checks.
3) Document reliability tests: deterministic replays; idempotent import; retry behaviors and timeouts; worker restart resilience.
4) Document security practices: API key rotation, secret management via environment, audit logging scope.
5) Document accessibility checklist aligned with UI outline.
6) Capture observability signals and metrics; ensure they are emitted where applicable.

Acceptance criteria:
- Calibration on toy dataset passes; steps are unambiguous and repeatable.
- Load test of toy scale passes; resilience verified via worker restart test.

MCP usage notes:
- Octocode: search exemplar validation playbooks and load testing approaches (if connected).
- SequentialThinking: document risk mitigations and residual issues; log decisions.
- Context7: optional references for reliability/security patterns if connected; proceed with contracts above if not.