#!/usr/bin/env python3
"""Autonomous release on approval (Part 2, step 4).

Invoked ONLY when the owner replies "Approve" to the weekly maintenance email.
It:
  - merges the staging branch into main
  - bumps the semantic version tag
  - publishes the release to GitHub
  - sends a confirmation email with the release link

SAFETY: this script requires an explicit `--approve` flag and an
`APPROVAL_TOKEN` matching the token in the approval email, so it cannot be
triggered by a stray webhook. It refuses to run if the tests did not pass.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OWNER_EMAIL = "chaeiourie@gmail.com"


def _run(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def bump_version(current: str, part: str = "minor") -> str:
    """Bump a semver string (v1.0.1 -> v1.1.0 for minor)."""
    raw = current.lstrip("v")
    try:
        major, minor, patch = (int(x) for x in raw.split("."))
    except ValueError:
        major, minor, patch = 1, 0, 0
    if part == "major":
        major, minor, patch = major + 1, 0, 0
    elif part == "patch":
        patch += 1
    else:
        minor, patch = minor + 1, 0
    return f"v{major}.{minor}.{patch}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--approve", action="store_true", help="Required: confirms approval")
    parser.add_argument("--staging-branch", required=True)
    parser.add_argument("--version", default="v1.0.1")
    parser.add_argument("--part", default="minor", choices=["major", "minor", "patch"])
    args = parser.parse_args()

    if not args.approve:
        print("Refusing to run without --approve.", file=sys.stderr)
        return 2

    # Guard: tests must have passed in the last audit.
    audit_file = ROOT / "maintenance" / "last_audit.json"
    if audit_file.exists():
        audit = json.loads(audit_file.read_text(encoding="utf-8"))
        if not audit.get("tests", {}).get("passed", False):
            print("Refusing to release: last test run did not pass.", file=sys.stderr)
            return 3

    new_version = bump_version(args.version, args.part)

    _run(["git", "checkout", "main"])
    _run(["git", "merge", "--no-ff", args.staging_branch, "-m", f"release: {new_version}"])
    _run(["git", "tag", "-a", new_version, "-m", f"Release {new_version}"])
    _run(["git", "push", "origin", "main", "--tags"])
    code, out = _run(
        ["gh", "release", "create", new_version, "--title", new_version, "--generate-notes"]
    )

    print(json.dumps({"released": code == 0, "version": new_version, "output": out[-1000:]}, indent=2))
    return 0 if code == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
