# Requirements — hmlv-data-contracts

Purpose
- Record Phase 1 completion (Data Contracts Pack) and link artifacts. No approvals requested per user instruction.

Sources
- [`hmlv_manufacturing_simulator_prd_v_0.md`](hmlv_manufacturing_simulator_prd_v_0.md)
- [`implementation_plan_2025-09-27T18-06-45Z.md`](implementation_plan_2025-09-27T18-06-45Z.md)
- [`agent_instructions/INSTRUCTION-2.md`](agent_instructions/INSTRUCTION-2.md)

Scope (Phase 1 — Data Contracts Pack)
- Author single authoritative JSON Schema
- Prepare toy CSV templates (one header row, minimal data)
- Define validation pipeline producing ValidationReport (file, row, column, message)
- Provide one negative dataset to exercise diagnostics

Produced Artifacts
- JSON Schema: [`schemas/project_config.schema.json`](schemas/project_config.schema.json)
- CSV templates:
  - [`examples/toy/products.csv`](examples/toy/products.csv)
  - [`examples/toy/routings.csv`](examples/toy/routings.csv)
  - [`examples/toy/machines.csv`](examples/toy/machines.csv)
  - [`examples/toy/operators.csv`](examples/toy/operators.csv)
  - [`examples/toy/setup_matrix.csv`](examples/toy/setup_matrix.csv)
  - [`examples/toy/demand.csv`](examples/toy/demand.csv)
  - [`examples/toy/calendars.csv`](examples/toy/calendars.csv)
  - [`examples/toy/mtbf_mttr.csv`](examples/toy/mtbf_mttr.csv)
  - [`examples/toy/yields.csv`](examples/toy/yields.csv)
  - [`examples/toy/skills.csv`](examples/toy/skills.csv)
- Negative dataset: [`examples/toy/negative/products_invalid.csv`](examples/toy/negative/products_invalid.csv)
- Validation pipeline (interfaces in engine):
  - [`engine/run.py`](engine/run.py)
- Validation runner:
  - [`tools/validate_toys.py`](tools/validate_toys.py)
- Validation output:
  - [`.artifacts/validation/validation_report.json`](.artifacts/validation/validation_report.json)

Acceptance Criteria (met)
- All toy CSVs parse; schema and CSV validators produce actionable diagnostics (file, row, column, message)
- Negative case fails with clear error: products.process_time_mean ≤ 0
- Validation report generated locally

Notes (KISS/YAGNI)
- Schema enforces numeric constraints and enums; full referential integrity checks deferred to later phases
- IANA timezones used for plant/calendars
- Simple row/column error format for UI/CI consumption

Next (Phase 2 preview)
- Extend referential checks (IDs across arrays)
- Implement dispatch/release/failures/rework semantics; KPI wiring