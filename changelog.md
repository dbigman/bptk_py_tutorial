# Changelog

All notable changes to this project are documented in this file.

## 2025-09-28 — Phase 1: Data Contracts Pack (completed / ready for review)

Summary:
- Completed authoritative JSON Schema for project import and validation: [`schemas/project_config.schema.json`](schemas/project_config.schema.json:1)
- Created authoritative toy CSV templates (products, routings, machines, operators, setup_matrix, demand, calendars, mtbf_mttr, yields, skills) under [`examples/toy/`](examples/toy/:1)
- Added a negative test dataset to exercise validation diagnostics: [`examples/toy/negative/products_invalid.csv`](examples/toy/negative/products_invalid.csv:1)
- Implemented validation pipeline:
  - Schema validation with Draft7 + FormatChecker and IANA timezone checks: [`engine/run.py::validate_project_config`](engine/run.py:213)
  - CSV validation with actionable row/column messages: [`engine/run.py::validate_csv_documents`](engine/run.py:338)
  - Referential integrity checks (including nested routing step checks): [`engine/run.py::validate_referential_integrity`](engine/run.py:463)
- Added structured ValidationReport and typed ValidationIssue model:
  - Validation models and parser: [`engine/validation.py`](engine/validation.py:1)
  - Structured runner and JSON report: [`tools/validate_toys.py`](tools/validate_toys.py:1) → `.artifacts/validation/validation_report.json`
- Timezone utilities (IANA helper & alias map): [`engine/timezones.py`](engine/timezones.py:1)
- Tests:
  - Basic validation pipeline test: [`tests/test_validation.py`](tests/test_validation.py:1) (1 passed)
- Spec-workflow:
  - Recorded Phase 1 artifacts under `.spec-workflow/specs/hmlv-data-contracts/` (requirements.md, design.md, tasks.md)
  - Approval requests submitted (requirements & design) — pending in dashboard (approval IDs recorded in repo activity)

Files changed/added (high level):
- engine/run.py (validators, referential checks, format checking)
- engine/validation.py (typed ValidationIssue / ValidationReport)
- engine/timezones.py (IANA helper)
- tools/validate_toys.py (runner; structured output)
- examples/toy/* (CSV templates)
- examples/toy/negative/products_invalid.csv
- .artifacts/validation/validation_report.json (generated artifact)
- .spec-workflow/specs/hmlv-data-contracts/* (requirements/design/tasks)
- TASK_LIST_INSTRUCTION_2.md (task log)
- tests/test_validation.py

Commit message (proposed)
- feat(data-contracts): add project_config JSON Schema, toy CSVs, and validation pipeline
- add structured ValidationReport and ValidationIssue dataclass; implement referential checks and IANA timezone helpers; add tests and spec-workflow artifacts; generate validation report

Notes
- Phase‑1 is ready for review and approval via the Spec Workflow dashboard. Two approval requests are pending.
- Phase‑2 follow-ups (optional / in-progress): enhance IANA whitelist, extend referential checks further, expose ValidationReport public API.