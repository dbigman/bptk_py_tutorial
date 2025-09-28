# Task List — Instruction 3 (Engine Scaffolding) 🛠️

Updated at: 2025-09-28T17:53:02Z (UTC)

Legend:
- ✅ = Done
- 🔄 = In Progress
- ⏳ = Pending / Manual

Summary (finalized)
- Core Phase‑2 starter implemented, validated, and documented. Only manual publishing remains.

Completed ✅
- ✅ Implement dispatch priority & selection — [`engine/dispatch.py`](engine/dispatch.py:1)
- ✅ Token-aware release control (CONWIP/POLCA) — [`engine/release_control.py`](engine/release_control.py:1)
- ✅ Deterministic run manifest + RNG + timeline artifact — [`engine/run.py`](engine/run.py:147)
- ✅ Failures RNG-aware next_downtime — [`engine/failures.py`](engine/failures.py:1)
- ✅ Rework loop with rework caps — [`engine/rework.py`](engine/rework.py:1)
- ✅ Artifact persistence and roundtrip tests — [`engine/run.py`](engine/run.py:209), [`tests/test_artifacts.py`](tests/test_artifacts.py:1)
- ✅ Validation report generated — `.artifacts/validation/validation_report.json`
- ✅ CI workflow skeleton added — [`.github/workflows/ci.yml`](.github/workflows/ci.yml:1)
- ✅ IANA alias whitelist expansion — [`engine/timezones.py`](engine/timezones.py:1)
- ✅ Additional CSV edge-case tests added — [`tests/test_csv_edgecases.py`](tests/test_csv_edgecases.py:1)

In Progress 🔄
- 🔄 Spec-workflow artifacts reviewed and tasks recorded — [`.spec-workflow/specs/hmlv-data-contracts`](.spec-workflow/specs/hmlv-data-contracts:1)
- 🔄 PR draft prepared and validation artifact attached — [`PR_DRAFT_PHASE1.md`](PR_DRAFT_PHASE1.md:1)

Pending / Manual ⏳
- ⏳ Open PR on remote repository and request reviewer approvals (manual step; requires credentials)
  - Suggested PR title: "feat(data-contracts): Phase‑1 Data Contracts Pack + Phase‑2 starters"
  - Include [`PR_DRAFT_PHASE1.md`](PR_DRAFT_PHASE1.md:1) as PR description and attach `.artifacts/validation/validation_report.json`

Next actions (what I will do when you tell me to proceed)
1. Open the PR on remote repo (requires your credentials / remote access) and set reviewers — manual step I cannot perform without credentials.
2. After PR is opened, poll spec-workflow approvals status and update tasks.md accordingly.
3. Expand IANA alias list further or accept external source if you request.

Notes
- All unit tests pass locally: `set PYTHONPATH=.&&pytest -q` → 9 passed.
- To reproduce validation report locally: `python tools/validate_toys.py` (writes `.artifacts/validation/validation_report.json`).
- Artifact smoke-test: `python -c "from engine.run import create_run_manifest, run_simulation; m=create_run_manifest('proj','{}',123); run_simulation(m)"`

Task provenance recorded in:
- [`TASK_LIST_INSTRUCTION_2.md`](TASK_LIST_INSTRUCTION_2.md:1)
- [`TASK_LIST_INSTRUCTION_3.md`](TASK_LIST_INSTRUCTION_3.md:1)
- Spec-workflow: `.spec-workflow/specs/hmlv-data-contracts/*`

File updated by: Roo — completed automation steps; awaiting manual PR open.