# Schema trade-offs and decisions

Source: implementation_plan_2025-09-27T18-06-45Z.md

Overview:
- This note records concise design decisions made while authoring the Phase‑1 project import JSON Schema and toy datasets.
- Principles applied: KISS (Keep It Simple, Stupid) and YAGNI (You Aren't Gonna Need It).

Decisions:
- Single authoritative schema: use `schemas/project_config.schema.json` as the canonical source of truth to avoid divergent validations.
- Minimal required fields: require only core keys (plant, products, routings, machines) to keep imports lightweight for MVP.
- Referential integrity deferred: cross-array ID resolution (e.g., product_id referenced in routings) is deferred to a focused Python validator to provide clearer, actionable errors.
- Numeric constraints enforced: process_time_mean > 0, setup_time >= 0, yield_rate in (0,1] implemented at schema/validator level.
- Timezones: prefer IANA timezone strings on plant and calendars to prepare for scheduling and PM windows.
- Validation format: errors emitted as `file:{name},row:{n},column:{col},message:{text}` for easy UI/CI consumption.

Spec-workflow mapping:
- Requirements: hmlv_manufacturing_simulator_prd_v_0.md
- Design: schemas/project_config.schema.json (this artifact)
- Tasks: examples/toy CSV templates + negative test
- Implementation: engine/run.py validators + tools/validate_toys.py

Produced artifacts (Phase‑1):
- schemas/project_config.schema.json
- examples/toy/{products,routings,machines,operators,setup_matrix,demand,calendars,mtbf_mttr,yields,skills}.csv
- examples/toy/negative/products_invalid.csv
- tools/validate_toys.py
- engine/run.py (validate_csv_documents, validate_project_config)
- .artifacts/validation/validation_report.json

Acceptance gates satisfied:
- Toy CSVs created and available under examples/toy/
- Validation runner executed and wrote .artifacts/validation/validation_report.json
- Negative test produced actionable error for products with non-positive process_time_mean

Next steps:
- Open PR including the above artifacts and run CI schema checks (swagger-cli / jsonschema where applicable).
- Implement referential integrity checks in engine/run.py or a dedicated validator module.
- Add a short spec-workflow approval note and attach this decision file for reviewers.

Author: Roo
Date: 2025-09-27T22:59:23Z