# INSTRUCTION-7 — UI Contracts and Outline (Phase 6)
Source: [implementation_plan_2025-09-27T18-06-45Z.md](implementation_plan_2025-09-27T18-06-45Z.md)

Objective:
- Create a UI outline with component responsibilities and API interactions.

Principles:
- KISS: skeleton component map; no implementation.
- YAGNI: avoid complex state management; define contracts only.

Deliverable:
- [ui/Outline.md](ui/Outline.md)

UI to API contracts:
- Data Wizard:
  - Uses POST validate/commit endpoints; shows per-file validation; uploads via multipart/form-data.
- Scenario Table:
  - Uses POST runs; displays seeds and parameters; links to run status.
- Results Dashboard:
  - Calls GET run, GET results; displays delta vs baseline; links to artifacts.
- Debrief View:
  - Calls POST debriefs and streams PDF.

Authoritative API references:
- [api.openapi.yaml](api/openapi.yaml)
- Endpoints: [api.post_validate_import(project_id: UUID, payload: ProjectImportPayload) -> ValidationReport](api/openapi.yaml:1), [api.post_commit_import(project_id: UUID, payload: ProjectImportPayload) -> ProjectSnapshot](api/openapi.yaml:1), [api.post_runs(project_id: UUID, scenario: ScenarioConfig) -> RunEnqueued](api/openapi.yaml:1), [api.get_run(project_id: UUID, run_id: RunId) -> RunStatus](api/openapi.yaml:1), [api.get_run_results(project_id: UUID, run_id: RunId) -> RunResultsIndex](api/openapi.yaml:1), [reports.debrief.render_debrief(run_id: RunId, template_id: DebriefTemplateId) -> ArtifactHandle](reports/debrief_template.md:1)

Steps:
1) Write [ui/Outline.md](ui/Outline.md) describing components: Data Wizard, Scenario Table, Results Dashboard, Debrief View.
2) Define navigation and state shape; specify data fetching contracts to API endpoints.
3) Provide example flows using sample responses (no code).

Accessibility:
- Align with WCAG 2.1 AA basics: color contrast, keyboard navigation, focus management, readable alt text.

Acceptance criteria:
- Outline accepted; mock flows traced end-to-end with sample responses.

MCP usage notes:
- Context7: reference Next.js 14 routing/data fetching contracts (if connected).
- Octocode: exemplar dashboards consuming REST endpoints (if connected).
- SequentialThinking: capture UX simplifications and accessibility notes.