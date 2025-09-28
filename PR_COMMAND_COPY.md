1 | Quick steps to create the draft PR (copy/paste commands)
2 | 
3 | 1) If using PowerShell, clear any GITHUB_TOKEN so gh can store credentials:
4 |    Remove-Item Env:GITHUB_TOKEN
5 |    (If using bash: export -n GITHUB_TOKEN or unset GITHUB_TOKEN)
6 | 2) Authenticate GH CLI (follow prompts):
7 |    gh auth login
8 | 3) (Optional) Ensure default repo is set to your origin:
9 |    gh repo set-default dbigman/bptk_py_tutorial
10 | 4) Commit any uncommitted changes (if present):
11 |    git add -A && git commit -m "chore: finalize changes for PR"
12 | 5) Create the draft PR (uses the prepared body file `PR_DRAFT_PHASE1.md`):
13 |    gh pr create --title "feat(data-contracts): Phase‑1 Data Contracts Pack + Phase‑2 starters" --body-file PR_DRAFT_PHASE1.md --base main --head phase1/data-contracts-pack --draft
14 | 
15 | If GH CLI still fails due to token scopes or permissions, open the PR manually on GitHub and paste the contents of [`PR_DRAFT_PHASE1.md`](PR_DRAFT_PHASE1.md:1) as the PR description.