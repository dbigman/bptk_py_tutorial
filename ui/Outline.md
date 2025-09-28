# UI Outline — HMLV Simulator (MVP)

Overview:
A lightweight React/Next.js frontend outline focusing on four primary views: Data Wizard, Scenario Table, Results Dashboard, and Debrief. Keep components small, stateless where possible, and fetch data from the REST API endpoints defined in [`api/openapi.yaml`](api/openapi.yaml:1).

Components and responsibilities:

- Data Wizard
  - Responsibilities: guide users through template selection, file upload, per-file validation, column mapping, and commit.
  - Key interactions:
    - Validate payload: POST /projects/{project_id}/import:validate
    - Commit import: POST /projects/{project_id}/import:commit
  - UI notes: show per-file row/column diagnostics (warnings/errors), allow re-upload, display checksum and snapshot_id on success.

- Scenario Table
  - Responsibilities: list scenarios for a project, allow cloning, parameter editing, and enqueue runs.
  - Key interactions:
    - Enqueue run: POST /projects/{project_id}/runs
    - Poll run status: GET /projects/{project_id}/runs/{run_id}
  - UI notes: show seed, status badge (queued/running/completed/failed), progress_pct, and quick actions (cancel/clone).

- Results Dashboard
  - Responsibilities: present KPIs, timelines, Gantt-like machine views, lead-time histograms, and comparison vs baseline.
  - Key interactions:
    - Fetch run status: GET /projects/{project_id}/runs/{run_id}
    - Fetch artifacts & KPIs: GET /projects/{project_id}/runs/{run_id}/results
  - UI notes: lazy-load heavy artifacts (CSV/JSON) and summarize KPIs in compact table with delta vs baseline.

- Debrief View
  - Responsibilities: request and stream the one-page debrief PDF; preview summary and provide download link.
  - Key interactions:
    - Request debrief: POST /projects/{project_id}/debriefs
  - UI notes: show artifact URL and expiration, provide copy/share buttons.

Navigation and page flow:
- Home / Projects: project cards and CTA "New Project"
- Project / Data Wizard → Scenarios → Results (select run) → Debrief
- Contextual breadcrumbs and simple left nav.

Minimal client state shape (example):
{
  "project": { "id": "...", "name": "Toy Plant", "snapshot_id": "..." },
  "scenarios": [ { "id": "...", "params": {...}, "seed": 123 } ],
  "selectedRun": { "run_id": "...", "status": "completed", "kpis": {...} }
}

Performance & accessibility:
- Keep pages SSR-friendly for core lists; lazy-load heavy charts and artifacts.
- Follow WCAG 2.1 AA basics: semantic HTML, keyboard focus, sufficient contrast.
- Avoid embedding large artifacts in state; use signed artifact URLs from API.

Developer notes:
- Frontend must treat API as authoritative; display server validation messages verbatim when helpful.
- Use small reusable components: FileUploader, ValidationTable, ScenarioForm, RunRow, KPIGrid, TimelineViewer.
- Feature toggles should be lightweight flags (not required for MVP).