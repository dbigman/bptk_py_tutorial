# Task List — Instruction 2 (Data Contracts Pack) 📦

Updated at: 2025-09-28T01:53:37Z

Legend:
- ✅ = Done
- 🔄 = In Progress
- ⏳ = Pending

Summary:
- ✅ Phase 1 implementation complete; validators, CSVs, schema, runner, tests all present.

Completed ✅
- ✅ Authoritative JSON Schema → [`schemas/project_config.schema.json`](schemas/project_config.schema.json:1)
- ✅ Toy CSVs → [`examples/toy/products.csv`](examples/toy/products.csv:1), [`examples/toy/routings.csv`](examples/toy/routings.csv:1), [`examples/toy/machines.csv`](examples/toy/machines.csv:1), [`examples/toy/operators.csv`](examples/toy/operators.csv:1), [`examples/toy/setup_matrix.csv`](examples/toy/setup_matrix.csv:1), [`examples/toy/demand.csv`](examples/toy/demand.csv:1), [`examples/toy/calendars.csv`](examples/toy/calendars.csv:1), [`examples/toy/mtbf_mttr.csv`](examples/toy/mtbf_mttr.csv:1), [`examples/toy/yields.csv`](examples/toy/yields.csv:1), [`examples/toy/skills.csv`](examples/toy/skills.csv:1)
- ✅ Negative test dataset → [`examples/toy/negative/products_invalid.csv`](examples/toy/negative/products_invalid.csv:1)
- ✅ Validation pipeline implemented → [`engine/run.py`](engine/run.py:1)
- ✅ Referential integrity checks (basic) → [`engine/run.py::validate_referential_integrity()`](engine/run.py:356)
- ✅ Nested routing step checks added → [`engine/run.py`](engine/run.py:1)
- ✅ IANA timezone helper added → [`engine/timezones.py`](engine/timezones.py:1)
- ✅ Validation models (typed) → [`engine/validation.py`](engine/validation.py:1)
- ✅ Validation runner & structured report → [`tools/validate_toys.py`](tools/validate_toys.py:1)
- ✅ Unit test → [`tests/test_validation.py`](tests/test_validation.py:1) (1 passed)

In Progress 🔄
- 🔄 Spec approvals requested (Requirements & Design) → approval IDs: approval_1759019487694_slmou72ra, approval_1759024072982_17o3ht86w (pending dashboard)
- 🔄 IANA whitelist/enhancement (expand fallback list & mapping) → basic helper added; whitelist refinement pending

Pending ⏳
- ⏳ Publish Phase‑1 PR and attach validation report [` .artifacts/validation/validation_report.json`](.artifacts/validation/validation_report.json:1)
- ⏳ Add more unit tests for edge cases and CSV parsing robustness

Next steps
1. Wait for dashboard approvals (poll or review in VS Code Spec Workflow).
2. Finish IANA whitelist enhancements and publish PR.
3. Move to Phase 2 tasks (dispatch rules, release control).