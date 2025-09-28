# PR Draft — Phase 1: Data Contracts Pack (HMLV Manufacturing Simulator)

Summary:
- This PR delivers the Phase‑1 "Data Contracts Pack": canonical JSON Schema, authoritative toy CSV templates, validation pipeline, typed ValidationReport, IANA timezone helpers, and Phase‑2 starter engine scaffolding (dispatch, release control, failures, rework, artifact persistence).
- All changes are minimal, follow KISS/YAGNI, and include unit tests and a short artifact smoke-test.

Key artifacts (for reviewers):
- Schema: [`schemas/project_config.schema.json`](schemas/project_config.schema.json:1)
- Toy CSV templates: [`examples/toy/products.csv`](examples/toy/products.csv:1), [`examples/toy/routings.csv`](examples/toy/routings.csv:1), [`examples/toy/machines.csv`](examples/toy/machines.csv:1), [`examples/toy/operators.csv`](examples/toy/operators.csv:1), [`examples/toy/setup_matrix.csv`](examples/toy/setup_matrix.csv:1), [`examples/toy/demand.csv`](examples/toy/demand.csv:1), [`examples/toy/calendars.csv`](examples/toy/calendars.csv:1), [`examples/toy/mtbf_mttr.csv`](examples/toy/mtbf_mttr.csv:1), [`examples/toy/yields.csv`](examples/toy/yields.csv:1), [`examples/toy/skills.csv`](examples/toy/skills.csv:1)
- Negative test dataset: [`examples/toy/negative/products_invalid.csv`](examples/toy/negative/products_invalid.csv:1)
- Validation pipeline & models: [`engine/run.py`](engine/run.py:1), [`engine/validation.py`](engine/validation.py:1), [`engine/timezones.py`](engine/timezones.py:1)
- Phase‑2 starter engine modules: [`engine/dispatch.py`](engine/dispatch.py:1), [`engine/release_control.py`](engine/release_control.py:1), [`engine/failures.py`](engine/failures.py:1), [`engine/rework.py`](engine/rework.py:1)
- Runner/tools: [`tools/validate_toys.py`](tools/validate_toys.py:1)
- Tests: [`tests/test_validation.py`](tests/test_validation.py:1), [`tests/test_validation_edgecases.py`](tests/test_validation_edgecases.py:1), [`tests/test_artifacts.py`](tests/test_artifacts.py:1)
- Task logs: [`TASK_LIST_INSTRUCTION_3.md`](TASK_LIST_INSTRUCTION_3.md:1), [`TASK_LIST_INSTRUCTION_2.md`](TASK_LIST_INSTRUCTION_2.md:1)

How to review (quick checklist):
1. Run unit tests: `set PYTHONPATH=.&&pytest -q` — all tests should pass locally. Current run: 6 passed.
2. Validate toy data: `python -c "from tools.validate_toys import main; main()"` or run `tools/validate_toys.py` to regenerate `.artifacts/validation/validation_report.json`.
3. Run smoke simulation: see [`engine/run.py`](engine/run.py:1) — example:
   - `python -c "from engine.run import create_run_manifest, run_simulation; m=create_run_manifest('proj','{}',123); print(run_simulation(m))"`
   - Verify `.artifacts/{run_id}/timeline.csv` exists.
4. Manual checks:
   - Open [`schemas/project_config.schema.json`](schemas/project_config.schema.json:1) and confirm required fields/constraints.
   - Inspect [`tools/validate_toys.py`](tools/validate_toys.py:1) for validation report output and location: `.artifacts/validation/validation_report.json`.

Notes for reviewers:
- Spec workflow artifacts recorded: `.spec-workflow/specs/hmlv-data-contracts/{requirements.md,design.md,tasks.md}` and `TASK_LIST_INSTRUCTION_3.md` documents the Phase‑1 and Phase‑2 task list with timestamps.
- Two approval requests have been created for Requirements and Design (pending in dashboard).
- Redis broker reachable locally (TCP 6379); `redis-cli` may not be installed in reviewers' environment — use `python` socket check or a client library as needed.
- Phase‑2 engine work is intentionally minimal and side-effect controlled to make review straightforward.

Merge checklist (recommended):
- [ ] Confirm tests pass in CI.
- [ ] Confirm `.artifacts/validation/validation_report.json` is attached to the PR (or generated in CI).
- [ ] Confirm spec approvals in dashboard (requirements & design) are resolved.
- [ ] Squash or keep commits per repo policy; use commit message from `commit-message.md`.

Review contact:
- Prepared by Roo — check `TASK_LIST_INSTRUCTION_3.md` for task provenance and timestamps.
