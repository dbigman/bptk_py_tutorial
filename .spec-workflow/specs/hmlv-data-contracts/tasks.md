# hmlv-data-contracts — tasks

Spec name: hmlv-data-contracts
Phase: 1 — Data Contracts Pack (Requirements/Design completed in repo docs; this tasks.md records implementation status)

Status: Phase 1 complete

Checklist:
- [x] Author authoritative JSON Schema ➜ [`schemas/project_config.schema.json`](schemas/project_config.schema.json:1)
- [x] Create toy CSV templates ➜ 
  - [`examples/toy/products.csv`](examples/toy/products.csv:1)
  - [`examples/toy/routings.csv`](examples/toy/routings.csv:1)
  - [`examples/toy/machines.csv`](examples/toy/machines.csv:1)
  - [`examples/toy/operators.csv`](examples/toy/operators.csv:1)
  - [`examples/toy/setup_matrix.csv`](examples/toy/setup_matrix.csv:1)
  - [`examples/toy/demand.csv`](examples/toy/demand.csv:1)
  - [`examples/toy/calendars.csv`](examples/toy/calendars.csv:1)
  - [`examples/toy/mtbf_mttr.csv`](examples/toy/mtbf_mttr.csv:1)
  - [`examples/toy/yields.csv`](examples/toy/yields.csv:1)
  - [`examples/toy/skills.csv`](examples/toy/skills.csv:1)
- [x] Add negative test dataset ➜ [`examples/toy/negative/products_invalid.csv`](examples/toy/negative/products_invalid.csv:1)
- [x] Implement validation pipeline functions (row/column diagnostics; schema validation) ➜ [`engine/run.py`](engine/run.py:1)
- [x] Create validation runner script ➜ [`tools/validate_toys.py`](tools/validate_toys.py:1)
- [x] Run local validation and produce report ➜ [`.artifacts/validation/validation_report.json`](.artifacts/validation/validation_report.json:1)
- [x] Document schema trade-offs and decisions ➜ [`docs/decisions/schema_tradeoffs.md`](docs/decisions/schema_tradeoffs.md:1)

Notes:
- ValidationReport entries include file/row/column/message per INSTRUCTION-2.
- JSON Schema enforces numeric constraints and enums; referential integrity checks deferred to later phase logic as documented.

Next (Phase 2 preview, not part of this spec):
- Implement dispatch rules, release control, failures, and rework semantics; wire KPIs.

Generated: 2025-09-27