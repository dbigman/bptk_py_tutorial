#!/usr/bin/env python3
"""
Auto-merge helper for GH pull requests.

Usage:
  python scripts/auto_merge_pr.py --repo my-github-username/bptk_py_tutorial --pr 1

This script polls GitHub (via the `gh` CLI) for:
- PR mergeable state
- latest commit status checks (state == "success")
- at least one approved review

When all conditions are satisfied it will attempt to merge the PR using
`gh pr merge` and delete the branch.

Notes:
- Requires `gh` CLI authenticated with sufficient permissions (repo, workflow).
- Runs until merged or until max_attempts reached.
- Default poll interval: 300s (5 minutes) as requested.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from typing import Optional


def run_cmd(cmd: list[str]) -> tuple[int, str, str]:
    """Run a CLI command and return (exit_code, stdout, stderr)."""
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except FileNotFoundError as ex:
        return 127, "", str(ex)


def get_pr_head_sha(owner: str, repo: str, pr: int) -> Optional[str]:
    code, out, err = run_cmd(["gh", "api", f"repos/{owner}/{repo}/pulls/{pr}"])
    if code != 0:
        print("ERROR: gh api failed:", err, file=sys.stderr)
        return None
    try:
        data = json.loads(out)
        return data.get("head", {}).get("sha")
    except Exception as ex:
        print("ERROR: parsing PR data:", ex, file=sys.stderr)
        return None


def get_commit_status_state(owner: str, repo: str, sha: str) -> Optional[str]:
    code, out, err = run_cmd(["gh", "api", f"repos/{owner}/{repo}/commits/{sha}/status"])
    if code != 0:
        print("ERROR: gh api commit status failed:", err, file=sys.stderr)
        return None
    try:
        data = json.loads(out)
        return data.get("state")
    except Exception as ex:
        print("ERROR: parsing commit status:", ex, file=sys.stderr)
        return None


def has_approved_review(owner: str, repo: str, pr: int) -> bool:
    code, out, err = run_cmd(["gh", "api", f"repos/{owner}/{repo}/pulls/{pr}/reviews"])
    if code != 0:
        print("ERROR: gh api reviews failed:", err, file=sys.stderr)
        return False
    try:
        reviews = json.loads(out)
        for r in reviews:
            state = r.get("state", "").upper()
            if state == "APPROVED":
                return True
    except Exception as ex:
        print("ERROR: parsing reviews:", ex, file=sys.stderr)
    return False


def is_pr_mergeable(owner: str, repo: str, pr: int) -> Optional[bool]:
    code, out, err = run_cmd(["gh", "pr", "view", f"{owner}/{repo}#{pr}", "--json", "mergeable"])
    if code != 0:
        print("ERROR: gh pr view failed:", err, file=sys.stderr)
        return None
    try:
        data = json.loads(out)
        # mergeable can be "MERGEABLE", "CONFLICTING", "UNKNOWN"
        val = data.get("mergeable")
        return val == "MERGEABLE"
    except Exception as ex:
        print("ERROR: parsing pr view:", ex, file=sys.stderr)
        return None


def attempt_merge(owner: str, repo: str, pr: int) -> bool:
    cmd = ["gh", "pr", "merge", str(pr), "--repo", f"{owner}/{repo}", "--merge", "--delete-branch"]
    code, out, err = run_cmd(cmd)
    if code == 0:
        print("Merged PR:", out)
        return True
    print("Merge attempt failed:", err or out, file=sys.stderr)
    return False


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True, help="owner/repo")
    p.add_argument("--pr", required=True, type=int, help="PR number")
    p.add_argument("--interval", type=int, default=300, help="Poll interval seconds (default 300)")
    p.add_argument("--max-attempts", type=int, default=48, help="Max poll attempts (default 48 -> 4 hours)")
    args = p.parse_args()

    if "/" not in args.repo:
        print("Repo must be in owner/repo form", file=sys.stderr)
        return 2
    owner, repo = args.repo.split("/", 1)
    pr = args.pr

    attempt = 0
    while attempt < args.max_attempts:
        attempt += 1
        print(f"[{attempt}] Checking PR {owner}/{repo}#{pr} ...")

        mergeable = is_pr_mergeable(owner, repo, pr)
        if mergeable is None:
            print("Could not determine mergeable state; retrying...")
        elif not mergeable:
            print("PR not mergeable yet (conflicts or unknown).")

        sha = get_pr_head_sha(owner, repo, pr)
        if not sha:
            print("Could not get head SHA; retrying...")
        else:
            status = get_commit_status_state(owner, repo, sha)
            print("Commit status:", status)
            checks_ok = status == "success"

            approved = has_approved_review(owner, repo, pr)
            print("Has approved review:", approved)

            if mergeable and checks_ok and approved:
                print("All conditions satisfied; attempting merge...")
                ok = attempt_merge(owner, repo, pr)
                if ok:
                    print("PR merged successfully.")
                    return 0
                else:
                    print("Merge failed; will retry.")
        if attempt >= args.max_attempts:
            break
        print(f"Sleeping {args.interval}s before next check...")
        time.sleep(args.interval)

    print("Max attempts reached or conditions not met. Exiting with code 1.")
    return 1


if __name__ == "__main__":
    sys.exit(main())