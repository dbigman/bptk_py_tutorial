# Design — hmlv-data-contracts

Purpose
- Record Phase 1 (Data Contracts Pack) completion, link artifacts, and define minimal technical design for validation/mapping. No approvals requested per current instruction.

Sources
- [`hmlv_manufacturing_simulator_prd_v_0.md`](hmlv_manufacturing_simulator_prd_v_0.md:1)
- [`implementation_plan_2025-09-27T18-06-45Z.md`](implementation_plan_2025-09-27T18-06-45Z.md:1)
- [`agent_instructions/INSTRUCTION-2.md`](agent_instructions/INSTRUCTION-2.md:1)

Artifacts (produced)
- JSON Schema: [`schemas/project_config.schema.json`](schemas/project_config.schema.json:1)
- CSV templates:
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
- Negative dataset: [`examples/toy/negative/products_invalid.csv`](examples/toy/negative/products_invalid.csv:1)
- Validation pipeline functions: [`engine.run.validate_project_config()`](engine/run.py:173), [`engine.run.validate_csv_documents()`](engine/run.py:209), [`engine.run.map_csvs_to_project()`](engine/run.py:252)
- Validation runner: [`tools/validate_toys.py`](tools/validate_toys.py:1)
- Validation output: [`.artifacts/validation/validation_report.json`](.artifacts/validation/validation_report.json:1)

Design Summary (KISS / YAGNI)
- Single authoritative JSON Schema validates shape and numeric constraints; referential integrity deferred to simple Python checks later (clear errors).
- Minimal row/column diagnostics format for CSV: `file:{name},row:{row},column:{column},message:{text}`.
- Deterministic, side‑effect‑free validators and mappers; no external services in Phase 1.

Schema Design
- Top‑level keys enforced: plant, products[], routings[], machines[], operators[], setup_matrix[], demand[], calendars[], mtbf_mttr[], yields[], skills[]. See [`schemas/project_config.schema.json`](schemas/project_config.schema.json:1).
- Numeric constraints:
  - process_time_mean > 0; process_time_sigma ≥ 0.
  - setup_time ≥ 0.
  - yield_rate ∈ (0,1].
  - capacity ≥ 1.
  - demand.quantity ≥ 1.
- Enums:
  - DispatchRule ∈ {EDD, SPT, ATC, ATCS, LSN}.
  - ReleasePolicy ∈ {CONWIP, POLCA}.
- Timezones: IANA strings for plant/calendars.

Validation Pipeline (Phase 1)
- JSON Schema Validation
  - Implementation: [`engine.run.validate_project_config()`](engine/run.py:173)
  - Uses Draft7Validator; errors collected via `iter_errors` and formatted using `error.path` and `error.message`.
  - Output emits `file:project_config.json,row:<n/a>,column:{json_path},message:{text}`.
- CSV Validation
  - Implementation: [`engine.run.validate_csv_documents()`](engine/run.py:209)
  - Checks per file:
    - products: process_time_mean present and > 0.
    - setup_matrix: setup_time present and ≥ 0.
    - yields: yield_rate in (0,1].
  - Rows numbered as DictReader rows (header=1, data starts=2).
- Mapping
  - Implementation: [`engine.run.map_csvs_to_project()`](engine/run.py:252)
  - Naive mapping of parsed CSV documents into ProjectConfig skeleton.

Runner & Artifacts
- [`tools/validate_toys.py`](tools/validate_toys.py:1) loads CSVs, runs CSV + schema validation, writes report to [`.artifacts/validation/validation_report.json`](.artifacts/validation/validation_report.json:1).
- Deterministic execution; no external dependencies beyond local files.

Context7 Guidance (jsonschema best practices)
- Use `Draft7Validator.iter_errors(instance)` and sort by `error.path` for stable output. Format paths via `list(error.path)` or `error.json_path` when available. Reference: python-jsonschema docs.
- Access `error.message` for human‑readable text; consider `ErrorTree` to group nested errors when introducing `anyOf/allOf` in later phases.
- Use `FormatChecker` for date‑time fields (e.g., demand.due_date). Proposal for Phase 2: enable `date-time` format checking with appropriate checker (Draft202012 or add checker for Draft7).

Octocode Exemplar Notes (patterns in OSS repos)
- Many pipelines model a `ValidationReport`/`ValidationIssue` dataclass with structured fields (file, row, column, message, severity). Phase 2 delta: introduce a typed `ValidationIssue` list instead of plain strings while keeping the same visible format for UI.
- Common practice sorts errors by path and groups by file; we will adopt this in Phase 2 when referential integrity checks are added.

Phase 2 Deltas (planned)
- Referential integrity:
  - Validate that IDs referenced across arrays exist (e.g., routings.product_id ∈ products, skills.operator_id ∈ operators).
  - Emit errors with concrete row and pointer (JSON path or CSV column).
- Format checking:
  - Enable `date-time` and `timezone` validation via `FormatChecker` and a whitelist for IANA zones.
- Error model:
  - Introduce `ValidationIssue` dataclass (file, row, column, message, severity) and aggregate into `ValidationReport`.
- Reporting:
  - Sort errors by (file, row, column); optionally emit `json_path` alongside column for schema validations.

Non‑Goals (Phase 1)
- Remote `$ref` resolution.
- DB‑level JSONB constraints (Postgres).
- Full calendar overlap detection.

Traceability to Implementation Plan & PRD
- Contracts referenced in Implementation Plan (engine.run/validate, map) are implemented: [`engine.run.validate_project_config()`](engine/run.py:173), [`engine.run.map_csvs_to_project()`](engine/run.py:252).
- PRD scope for data ingest and validation is satisfied with minimal, actionable diagnostics and toy datasets.

Status
- Phase 1 (Data Contracts Pack) completed and recorded; this design.md links artifacts and defines next deltas for Phase 2.