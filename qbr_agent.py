#!/usr/bin/env python3
"""QBR Narrator Agent — command-line entry point.

For non-technical users there is also a web UI (see the app/ folder and the
README). This CLI is the engine's control surface and supports:

    python qbr_agent.py --test-keys        # pre-flight: which API keys are active
    python qbr_agent.py --demo             # generate a sample bundle locally
    python qbr_agent.py --serve            # print the web UI start command

Nothing is ever emailed to a customer without explicit approval, and TEST_MODE
(default true) forces the free local adapter.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Load .env if python-dotenv is available (optional).
try:  # pragma: no cover - optional dependency
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover
    pass

from engine.qbr_engine import QbrInput, dispatch_bundle, generate_bundle


def _key_status() -> dict:
    keys = {
        "ANTHROPIC_API_KEY": "Anthropic Claude (deck text & tone)",
        "ELEVENLABS_API_KEY": "ElevenLabs (voice narration & cloning)",
        "SENDGRID_API_KEY": "SendGrid email adapter",
        "MAILCHIMP_API_KEY": "Mailchimp email adapter",
        "SMTP_HOST": "SMTP email adapter",
    }
    status = {}
    for key, label in keys.items():
        present = bool(os.getenv(key, "").strip())
        status[key] = {"label": label, "active": present}
    return status


def cmd_test_keys() -> int:
    print("QBR Narrator Agent — pre-flight key check")
    print("-" * 52)
    status = _key_status()
    for key, info in status.items():
        mark = "ACTIVE  " if info["active"] else "missing "
        print(f"  [{mark}] {key:<22} {info['label']}")
    adapter = os.getenv("EMAIL_ADAPTER", "local")
    test_mode = os.getenv("TEST_MODE", "true")
    print("-" * 52)
    print(f"  Email adapter : {adapter}")
    print(f"  TEST_MODE     : {test_mode}")
    print(f"  Budget guard  : MAX_COST_PER_DECK=${os.getenv('MAX_COST_PER_DECK', '0.50')}")
    if not status["ANTHROPIC_API_KEY"]["active"] or not status["ELEVENLABS_API_KEY"]["active"]:
        print("\n  Note: without both AI keys the agent runs in local-template mode")
        print("  (deck + checklist still generate; audio narration is skipped).")
    return 0


def cmd_demo() -> int:
    qbr = QbrInput(
        customer_name="Acme Corp",
        target_language="en",
        recipient_email="customer@example.com",
        raw_notes=(
            "Acme achieved a 22% increase in weekly active users this quarter. "
            "We saved their team 40 hours of manual reporting. "
            "Risk: their renewal is in 90 days and a competitor is circling. "
            "Next quarter: expand to the EMEA team and set up a security review."
        ),
    )
    bundle = generate_bundle(qbr)
    out = Path(os.getenv("OUTPUT_DIR", "./output"))
    print("Bundle generated (local template mode):")
    print(f"  Deck      : {out / 'acme-corp_qbr_deck.html'}")
    print(f"  Checklist : {out / 'SETUP_AND_SUBSCRIPTION_CHECKLIST.md'}")
    print(f"  Slides    : {len(bundle.slides)}")
    print(f"  Language  : {bundle.language}")
    print(f"  Gaps found: {bundle.decision_log['gaps']}")
    print("\nDispatch is gated: nothing is emailed until a Customer Success Manager approves.")
    return 0


def cmd_serve() -> int:
    print("Start the web UI with:")
    print("  npm install && npm run dev")
    print("Then open the local URL it prints (default http://localhost:5173).")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="QBR Narrator Agent")
    parser.add_argument("--test-keys", action="store_true", help="Check which API keys are active")
    parser.add_argument("--demo", action="store_true", help="Generate a sample bundle locally")
    parser.add_argument("--serve", action="store_true", help="Show how to start the web UI")
    parser.add_argument("--json", action="store_true", help="Machine-readable output for --test-keys")
    args = parser.parse_args(argv)

    if args.test_keys:
        if args.json:
            print(json.dumps(_key_status(), indent=2))
        return cmd_test_keys()
    if args.demo:
        return cmd_demo()
    if args.serve:
        return cmd_serve()

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
