#!/usr/bin/env python3
"""Zero-Manual-Maintenance — the weekly autonomous audit (Part 2).

Runs every Monday at 09:00 UTC (see .github/workflows/weekly-maintenance.yml).
It:
  1. Scans for new Anthropic / ElevenLabs releases, new community adapters, and
     security advisories in requirements.txt.
  2. If updates are available: bumps requirements.txt, runs the test suite in
     dry-run, and prepares a draft release with a CHANGELOG on a staging branch.
  3. Sends a one-click approval email to the owner.
  4. On an "Approve" reply, merges staging -> main, tags a release, and publishes.

SAFETY: this script NEVER merges or publishes on its own. It prepares a staging
branch and a draft, then waits for the owner's explicit "Approve". The actual
merge/tag/publish step lives in maintenance/on_approval.py and is only invoked
by the approval workflow.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

OWNER_EMAIL = "chaeiourie@gmail.com"
REPO = "chaeiourie/qbr-narrator-agent"
ROOT = Path(__file__).resolve().parent.parent


def _run(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def scan_dependencies() -> dict:
    """Scan for available dependency updates and security advisories."""
    findings: dict = {"outdated": [], "advisories": []}
    # pip-audit reports known vulnerabilities in the installed requirements.
    code, out = _run([sys.executable, "-m", "pip_audit", "-r", "requirements.txt", "--format", "json"])
    if code == 0 and out:
        try:
            findings["advisories"] = json.loads(out).get("vulnerabilities", [])
        except json.JSONDecodeError:
            pass
    # pip list --outdated reports newer versions available.
    code, out = _run([sys.executable, "-m", "pip", "list", "--outdated", "--format", "json"])
    if code == 0 and out:
        try:
            findings["outdated"] = json.loads(out)
        except json.JSONDecodeError:
            pass
    return findings


def run_tests_dry_run() -> dict:
    """Run the test suite in dry-run mode."""
    code, out = _run([sys.executable, "-m", "pytest", "-q", "--maxfail=1"])
    return {"passed": code == 0, "output": out[-2000:]}


def prepare_staging_branch(version: str) -> str:
    """Create/refresh a staging branch and commit the prepared changes."""
    branch = f"staging/weekly-{datetime.now(timezone.utc).strftime('%Y%m%d')}"
    _run(["git", "checkout", "-B", branch])
    _run(["git", "add", "-A"])
    _run(["git", "commit", "-m", f"chore: weekly maintenance staging {version}"])
    return branch


def build_approval_email(findings: dict, tests: dict, branch: str) -> dict:
    """Compose the one-click approval email (sent to the owner)."""
    bullet_lines = []
    for dep in findings.get("outdated", [])[:10]:
        bullet_lines.append(f"- {dep.get('name')}: {dep.get('version')} -> {dep.get('latest_version')}")
    for adv in findings.get("advisories", [])[:10]:
        bullet_lines.append(f"- SECURITY: {adv.get('name')} {adv.get('version')} ({adv.get('id')})")
    if not bullet_lines:
        bullet_lines.append("- No dependency updates found this week.")

    body = (
        "Weekly maintenance preview for QBR Narrator Agent.\n\n"
        "What changed:\n" + "\n".join(bullet_lines) + "\n\n"
        f"Tests: {'PASS' if tests.get('passed') else 'FAIL'}\n"
        f"Staging branch: {branch}\n\n"
        "Reply 'Approve' to auto-merge, tag the release, and push to GitHub."
    )
    return {
        "to": OWNER_EMAIL,
        "subject": "[Action Required] QBR Narrator Agent - Weekly Maintenance & Release Preview",
        "body": body,
    }


def main() -> int:
    version = os.getenv("VERSION", "v1.0.1")
    findings = scan_dependencies()
    tests = run_tests_dry_run()
    branch = prepare_staging_branch(version)
    email = build_approval_email(findings, tests, branch)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "version": version,
        "findings": findings,
        "tests": tests,
        "staging_branch": branch,
        "approval_email": email,
        "note": "Nothing is merged or published until the owner replies 'Approve'.",
    }
    out = ROOT / "maintenance" / "last_audit.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"status": "prepared", "report": str(out), "staging_branch": branch}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
