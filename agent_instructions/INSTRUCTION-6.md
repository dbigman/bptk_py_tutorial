# INSTRUCTION-6 — KPI Computation and Reporting (Phase 5)
Source: [implementation_plan_2025-09-27T18-06-45Z.md](implementation_plan_2025-09-27T18-06-45Z.md)

Objective:
- Define KPI specifications; implement aggregation and CSV export; render debrief to PDF.

Principles:
- KISS: limit to MVP KPIs; clear units and sampling windows.
- YAGNI: avoid complex statistical treatments beyond percentile p90.

Deliverables:
- [kpis/spec.md](kpis/spec.md)
- [reports/debrief_template.md](reports/debrief_template.md)
- CSV artifact for KPI table (stored via artifact store convention)

Authoritative interfaces:
- [kpis.compute.compute_kpis(run_id: RunId) -> KPIReport](kpis/compute.py:12)
- [kpis.compute.export_kpis_csv(report: KPIReport, destination: ArtifactPath) -> ArtifactHandle](kpis/compute.py:22)
- [reports.debrief.render_debrief(run_id: RunId, template_id: DebriefTemplateId) -> ArtifactHandle](reports/debrief_template.md:1)

KPI definitions (spec pointers):
- OTD %: due_date ≥ completion_time; sampling: all jobs.
- Lead time avg/p90: completion_time − release_time; sampling: all jobs; p90: percentile.
- WIP: time-averaged job count in system; units: jobs.
- Machine/labor utilization: busy_time / available_time; units: %.
- Setup hours: sum of setup_time across machines; units: hours.
- Scrap/rework rate: rework_count / inspected_count; units: %.
- Full formulas enumerated in [kpis/spec.md](kpis/spec.md).

Storage contracts:
- Artifact convention: s3://{bucket}/{project_id}/{run_id}/{kind}/...
- Use interfaces:
  - [engine.run.store_artifact(run_id: RunId, kind: ArtifactKind, payload: Bytes, media_type: str) -> ArtifactHandle](engine/run.py:60)
  - [engine.run.load_artifact(handle: ArtifactHandle) -> Bytes](engine/run.py:68)

Steps:
1) Author [kpis/spec.md](kpis/spec.md) with formula definitions, sampling windows, units, and any tolerance thresholds used in validations.
2) Implement aggregation via [kpis.compute.compute_kpis(run_id: RunId) -> KPIReport](kpis/compute.py:12); ensure KPIReport includes all fields referenced by debrief template.
3) Export CSV via [kpis.compute.export_kpis_csv(report: KPIReport, destination: ArtifactPath) -> ArtifactHandle](kpis/compute.py:22); persist using artifact store convention.
4) Prepare [reports/debrief_template.md](reports/debrief_template.md) with placeholders bound to KPIReport fields; plan Markdown-to-PDF rendering pipeline (WeasyPrint; no code here).
5) Verify KPIs on toy dataset; confirm outputs match spec fields and units.

Acceptance criteria:
- KPIs printed as compact table and written to CSV.
- Debrief renders to PDF via pipeline and references KPI placeholders correctly.

Observability:
- Logs include request_id, run_id, project_id, scenario_id, seed, phase, duration_ms, outcome.
- Metrics emitted: runs_completed, run_duration_seconds; optionally kpi_compute_duration_seconds.

MCP usage notes:
- Octocode: find exemplar KPI aggregation layouts and CSV export patterns (if connected; otherwise proceed with local spec).
- SequentialThinking: record rationale on sampling windows and tolerance thresholds, note any deviations.
- Context7: optional references for reporting patterns if available; if not connected, proceed with interfaces above.