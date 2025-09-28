# INSTRUCTION-2 — Data Contracts Pack (Phase 1)
Source: [implementation_plan_2025-09-27T18-06-45Z.md](implementation_plan_2025-09-27T18-06-45Z.md)

Objective:
- Author project import JSON Schema and prepare toy datasets.
- Define validation pipeline producing ValidationReport.

Principles:
- KISS: single authoritative schema; minimal required fields.
- YAGNI: avoid optional features not used in MVP.

Data contracts:
- JSON Schema file: [schemas/project_config.schema.json](schemas/project_config.schema.json)
  - Top-level keys: plant, products[], routings[], machines[], operators[], setup_matrix[], demand[], calendars[], mtbf_mttr[], yields[], skills[].
  - Constraints:
    - Referential integrity across arrays (ids must resolve).
    - Numeric constraints: process_time_mean > 0; setup_time ≥ 0; yield_rate ∈ (0,1].
    - Enums: dispatch rules ∈ {EDD, SPT, ATC, ATCS, LSN}; release policy ∈ {CONWIP, POLCA}.
    - Timezones: IANA (e.g., "America/La_Paz").
- CSV template headers (one authoritative header row each):
  - [examples/toy/products.csv](examples/toy/products.csv), [examples/toy/routings.csv](examples/toy/routings.csv), [examples/toy/machines.csv](examples/toy/machines.csv), [examples/toy/operators.csv](examples/toy/operators.csv), [examples/toy/setup_matrix.csv](examples/toy/setup_matrix.csv), [examples/toy/demand.csv](examples/toy/demand.csv), [examples/toy/calendars.csv](examples/toy/calendars.csv), [examples/toy/mtbf_mttr.csv](examples/toy/mtbf_mttr.csv), [examples/toy/yields.csv](examples/toy/yields.csv), [examples/toy/skills.csv](examples/toy/skills.csv).
- Experiment configuration: [experiments.yaml](experiments.yaml) defining scenario parameters and sweeps.

Validation pipeline interfaces (authoritative):
- [engine.run.validate_project_config(doc: JSON) -> ValidationReport](engine/run.py:76)
- [engine.run.map_csvs_to_project(documents: list[CSV]) -> ProjectConfig](engine/run.py:84)

ValidationReport expectations:
- Fields: valid: bool; warnings[]; errors[].
- Each error/warning entry: file, row, column, message.

Steps:
1) Write [schemas/project_config.schema.json](schemas/project_config.schema.json) with constraints and cross-file references.
2) Prepare toy CSVs with the exact headers listed; include minimal rows for baseline.
3) Define validation pipeline producing ValidationReport via the interfaces above (no implementation code here).
4) Add one negative test dataset to exercise validation diagnostics.

Acceptance criteria:
- All toy CSVs validate successfully.
- One negative test fails with actionable errors (row/column references present).
- Example ValidationReport contains warnings/errors as specified.

MCP usage notes:
- Context7: reference JSON Schema best practices (if connected).
- Octocode: find exemplar schemas and validation report formats in similar repos.
- SequentialThinking: document schema trade-offs and field naming decisions.