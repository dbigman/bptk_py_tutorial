Remote repo creation instructions — run locally

1. Edit the helper script and set your GitHub username:
   - Open: scripts/create_and_push_repo.sh
   - Replace USERNAME="your-github-username" with your actual GitHub username.

2. Ensure GH CLI is authenticated and can create repos:
   - gh auth login
   - gh auth status
   - Token must have repo/create permission for private repos.

3. Run the helper (Bash):
   - sh scripts/create_and_push_repo.sh
   - This will:
     - create a private repo named bptk_py_tutorial under your account
     - add a remote origin (if not present)
     - push the current branch (phase1/data-contracts-pack)

4. If you prefer manual commands, run:
   - git checkout phase1/data-contracts-pack
   - git push -u origin phase1/data-contracts-pack
   - gh repo create my-github-username/bptk_py_tutorial --private --source . --remote origin --push

5. Create PR (after repo exists and branch is pushed):
   - gh pr create --title "feat(data-contracts): Phase‑1 Data Contracts Pack + Phase‑2 starters" --body-file PR_DRAFT_PHASE1.md --base main --head phase1/data-contracts-pack

6. If gh CLI returns permission errors:
   - Ensure your PAT (or GH app token) includes repo:create and repo scopes.
   - Alternatively create the repository in the GitHub web UI and push the branch manually.

7. After PR is open:
   - Share the PR URL here and I will poll spec-workflow approvals and update the task list.

End.