#!/bin/sh
# Script to create GitHub repo and push current branch using gh CLI
# Edit USERNAME before running

USERNAME="your-github-username"
REPO="bptk_py_tutorial"
VISIBILITY="private"
BRANCH="phase1/data-contracts-pack"

set -e

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI not found. Install from https://cli.github.com/"
  exit 1
fi

echo "Creating repository $USERNAME/$REPO (visibility=$VISIBILITY)"
gh repo create "$USERNAME/$REPO" --"$VISIBILITY" --source . --remote origin --push --confirm || {
  echo "gh repo create failed. Ensure you are authenticated: gh auth login"
  exit 1
}

echo "Ensuring branch $BRANCH exists locally"
git checkout "$BRANCH" || git switch -c "$BRANCH"

echo "Pushing branch to origin"
git push -u origin "$BRANCH"

echo "Repository created and branch pushed: https://github.com/$USERNAME/$REPO"

# PowerShell alternative (Windows) - save as scripts\create_and_push_repo.ps1 and edit $Username
# $Username = 'your-github-username'
# $Repo = 'bptk_py_tutorial'
# gh repo create "$Username/$Repo" --private --source . --remote origin --push --confirm