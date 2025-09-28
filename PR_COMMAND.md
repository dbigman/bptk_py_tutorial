PR creation command and instructions

Steps to create the draft PR (copy/paste):

1) Ensure GH CLI is authenticated:
   - Run: gh auth login
   - If you see "GITHUB_TOKEN is being used", clear it in PowerShell:
     Remove-Item Env:GITHUB_TOKEN

2) (optional) Ensure the default repo is set to your origin:
   - gh repo set-default dbigman/bptk_py_tutorial

3) Create the draft PR using the prepared PR body file:
   gh pr create --title "feat(data-contracts): Phase‑1 Data Contracts Pack + Phase‑2 starters" --body-file PR_DRAFT_PHASE1.md --base main --head phase1/data-contracts-pack --draft

Notes:
- The PR body is in [`PR_DRAFT_PHASE1.md`](PR_DRAFT_PHASE1.md:1).
- The task list was updated in [`TASK_LIST_INSTRUCTION_3.md`](TASK_LIST_INSTRUCTION_3.md:1).
- If GH CLI still fails due to token scopes or auth, open the PR manually on GitHub using the UI and paste the contents of [`PR_DRAFT_PHASE1.md`](PR_DRAFT_PHASE1.md:1) as the description.
