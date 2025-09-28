feat(data-contracts): add project_config schema, toy CSVs, and validation pipeline

- Add authoritative JSON Schema for project import and validation.
- Add toy CSV templates and a negative test dataset for diagnostics.
- Implement schema + CSV validators, referential checks, and structured ValidationReport.
- Add typed ValidationIssue/ValidationReport models and timezone utilities.
- Add validation runner, tests, and spec-workflow artifacts for Phase 1.

Refs: .spec-workflow/specs/hmlv-data-contracts, .artifacts/validation/validation_report.json