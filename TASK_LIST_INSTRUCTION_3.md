# Task List — Instruction 3 (Engine Scaffolding) 🛠️

Updated at: 2025-09-28T19:12:54Z (UTC)

Legend:
- ✅ = Done
- 🔄 = In Progress / Current
- ⏳ = Pending / Manual

Snapshot summary
- Core Phase‑2 starter implemented, validated, documented, and pushed to your origin. Only PR creation and external approvals remain manual.

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
- ✅ Repo rebrand and fork prep — replaced "transentis" → "dbigman" in docs/notebooks, updated [`pyproject.toml`](pyproject.toml:1), [`LICENSE`](LICENSE:1) and helper scripts [`scripts/create_and_push_repo.sh`](scripts/create_and_push_repo.sh:1)
- ✅ Git remotes and branch metadata updated to point at your origin — [`.git/config`](.git/config:1)
- ✅ Tests executed locally — `pytest` → 9 passed
- ✅ Formatting applied (black + ruff --fix) and style commit created
- ✅ Changes committed and pushed to origin branch `phase1/data-contracts-pack`

In Progress 🔄
- 🔄 Review remaining linter findings (flake8) for project files — follow-up fixes may be applied incrementally.
- 🔄 Spec-workflow artifacts reviewed and tasks recorded — [`.spec-workflow/specs/hmlv-data-contracts`](.spec-workflow/specs/hmlv-data-contracts:1)
- ✅ PR draft prepared — [`PR_DRAFT_PHASE1.md`](PR_DRAFT_PHASE1.md:1)

Pending / Manual ⏳
- ✅ Open PR on remote repository — Draft created: https://github.com/dbigman/bptk_py_tutorial/pull/1
  - Suggested PR title: "feat(data-contracts): Phase‑1 Data Contracts Pack + Phase‑2 starters"
  - Include [`PR_DRAFT_PHASE1.md`](PR_DRAFT_PHASE1.md:1) as PR description and attach `.artifacts/validation/validation_report.json`
- ⏳ Confirm external links and hosted prototypes replacement (e.g., redirects from `prototypes.transentis.com`) if you want them changed or removed.

Next actions (what I will do when you tell me to proceed)
1. Create/open the PR on the remote repo (requires your credentials or you can run the supplied command). Example (run locally or I can run if you provide auth):
   - [`gh pr create --title "feat(data-contracts): Phase‑1 Data Contracts Pack + Phase‑2 starters" --body-file PR_DRAFT_PHASE1.md --base main --head phase1/data-contracts-pack --draft`](PR_DRAFT_PHASE1.md:1)
2. After PR is opened, poll spec-workflow approvals status and update tasks/this file accordingly.
3. Triage remaining flake8 findings and apply safe, targeted fixes (or accept some issues as legacy examples in notebooks).
4. Optionally add an `upstream` remote to track original repository:
   - `git remote add upstream https://github.com/transentis/bptk_py_tutorial.git`

Notes
- All unit tests pass locally: `set PYTHONPATH=.&&pytest -q` → 9 passed.
- To reproduce validation report locally: `python tools/validate_toys.py` (writes `.artifacts/validation/validation_report.json`).
- Artifact smoke-test: `python -c "from engine.run import create_run_manifest, run_simulation; m=create_run_manifest('proj','{}',123); run_simulation(m)"`
- Lint summary: `flake8` run produced remaining style warnings in project files (notebooks and some legacy examples). I recommend addressing these incrementally; automated fixes applied already via `ruff --fix` and `black`.

Task provenance recorded in:
- [`TASK_LIST_INSTRUCTION_2.md`](TASK_LIST_INSTRUCTION_2.md:1)
- [`TASK_LIST_INSTRUCTION_3.md`](TASK_LIST_INSTRUCTION_3.md:1)
- Spec-workflow: `.spec-workflow/specs/hmlv-data-contracts/*`

File updated by: Roo — automation and formatting completed; awaiting your signal to open PR and finish reviewer flow.