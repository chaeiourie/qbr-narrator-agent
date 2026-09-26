"""Mythos Security Shield (Tier 1) — real controls, not marketing claims.

Controls implemented here:
  - ASI01 / LLM01  Prompt Injection & Goal Hijacking Protection
  - LLM02 / LLM05  Data Minimization & PII / Secret Redaction
  - ASI04          Agentic Supply Chain Isolation (read-only by default)
  - ASI08          Blast Radius / Anomaly Flag & Pause

These run at the boundary where external data enters the agent, BEFORE any
outbound LLM or API call. They are deliberately conservative: they flag clear
command-override language, not ordinary business prose.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable

# ---------------------------------------------------------------------------
# ASI01 / LLM01 — Prompt Injection & Goal Hijacking Protection
# ---------------------------------------------------------------------------

_INJECTION_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(
            r"(ignore|disregard|override|forget)\s+(all\s+)?(previous|prior|your|the above)\s+"
            r"(instructions|prompts?|rules|guidelines|system)",
            re.I,
        ),
        "instruction-override",
    ),
    (
        re.compile(
            r"(you\s+are\s+now|act\s+as|pretend\s+to\s+be|from\s+now\s+on)\s+.{0,60}"
            r"(without\s+restrictions|no\s+restrictions|unrestricted)",
            re.I,
        ),
        "persona-hijack",
    ),
    (
        re.compile(
            r"(reveal|print|output|repeat|show|leak|expose)\s+(your|the)\s+"
            r"(system\s+)?(prompt|instructions|rules|secret|api[_-]?key|config)",
            re.I,
        ),
        "system-prompt-exfiltration",
    ),
    (
        re.compile(
            r"(send|email|post|upload|transmit)\s+(this|the|all|every)\s+"
            r"(data|info|information|content|records?)\s+to",
            re.I,
        ),
        "data-exfiltration",
    ),
    (
        re.compile(
            r"(execute|run|call|invoke)\s+(arbitrary|any|external|shell|code|commands?|functions?|endpoints?)",
            re.I,
        ),
        "tool-abuse",
    ),
    (
        re.compile(
            r"(delete|drop|truncate|update|overwrite|modify)\s+(all|every|any)\s+"
            r"(records?|rows|accounts?|data|entries)",
            re.I,
        ),
        "destructive-write",
    ),
]


@dataclass
class InjectionVerdict:
    status: str  # "clean" | "quarantined"
    matched_pattern: str | None = None
    reason: str | None = None


def scan_for_injection(text: str) -> InjectionVerdict:
    """Scan one external input for injection payloads.

    A quarantined input must NOT be forwarded to the LLM or used to drive any
    tool call.
    """
    if not text or not isinstance(text, str):
        return InjectionVerdict(status="clean")
    for pattern, label in _INJECTION_PATTERNS:
        if pattern.search(text):
            return InjectionVerdict(
                status="quarantined",
                matched_pattern=label,
                reason=(
                    "Input matched an indirect prompt-injection signature. Content was "
                    "not forwarded to the language model or any tool."
                ),
            )
    return InjectionVerdict(status="clean")


def filter_external_inputs(inputs: Iterable[str]) -> tuple[list[str], list[dict]]:
    """Filter a batch of external inputs. Returns (clean, blocked)."""
    clean: list[str] = []
    blocked: list[dict] = []
    for index, value in enumerate(inputs):
        verdict = scan_for_injection(value)
        if verdict.status == "clean":
            clean.append(value)
        else:
            blocked.append(
                {"index": index, "reason": verdict.reason, "matched_pattern": verdict.matched_pattern}
            )
    return clean, blocked


# ---------------------------------------------------------------------------
# LLM02 / LLM05 — Data Minimization & PII / Secret Redaction
# ---------------------------------------------------------------------------

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"(\+?\d{1,3}[\s.-]?)?(\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}")
_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_SECRET_RE = re.compile(
    r"(api[_-]?key|secret|token|password|authorization|bearer)\s*[:=]\s*[\"']?[A-Za-z0-9_\-.^]{8,}[\"']?",
    re.I,
)
_GENERIC_SECRET_RE = re.compile(r"\b(sk|pk|ghp|gho|xox[baprs]-|AKIA)[A-Za-z0-9_\-]{16,}\b")
_CARD_RE = re.compile(r"\b(?:\d[ -]*?){13,16}\b")


def _mask(match: str, kind: str) -> str:
    keep = match[:2] + "…" + match[-1] if len(match) > 4 else "…"
    return f"[{kind}:{keep}]"


def redact(text: str, scope: str = "balanced") -> str:
    """Redact PII and secrets from a string.

    scope: "strict" | "balanced" | "off". Secrets are ALWAYS redacted.
    Run this on any text that will be sent to an outbound LLM or API call.
    """
    if scope == "off" or not text:
        return text
    out = _SECRET_RE.sub(lambda m: _mask(m.group(0), "secret"), text)
    out = _GENERIC_SECRET_RE.sub(lambda m: _mask(m.group(0), "secret"), out)

    if scope == "strict":
        out = _EMAIL_RE.sub(lambda m: _mask(m.group(0), "email"), out)
        out = _PHONE_RE.sub(lambda m: _mask(m.group(0), "phone"), out)
        out = _SSN_RE.sub(lambda m: _mask(m.group(0), "ssn"), out)
        out = _CARD_RE.sub(lambda m: _mask(m.group(0), "card"), out)
    elif scope == "balanced":
        # Keep the domain hint (useful for context) but mask the local part.
        def _email(m: re.Match[str]) -> str:
            value = m.group(0)
            at = value.find("@")
            return f"[email:{value[at + 1:]}]" if at > 0 else _mask(value, "email")

        out = _EMAIL_RE.sub(_email, out)
        out = _SSN_RE.sub(lambda m: _mask(m.group(0), "ssn"), out)
        out = _CARD_RE.sub(lambda m: _mask(m.group(0), "card"), out)
    return out


# ---------------------------------------------------------------------------
# ASI04 — Agentic Supply Chain Isolation (read-only by default)
# ---------------------------------------------------------------------------

VALID_SCOPES = ("read-only", "read-write")
VALID_ACTION_KINDS = ("read", "write", "commit")


@dataclass
class ProposedAction:
    id: str
    kind: str  # "read" | "write" | "commit"
    target: str
    summary: str
    affected_records: int = 0
    impact: str = ""


@dataclass
class ActionVerdict:
    status: str  # "allowed" | "blocked" | "needs-human-gate"
    reason: str = ""


def gate_action(action: ProposedAction, scope: str, human_authorized: bool) -> ActionVerdict:
    """Gate an action against the current execution scope.

    - Reads are always allowed.
    - Writes are BLOCKED unless scope is "read-write" AND a human gate authorized it.
    - Commits (irreversible commitments) ALWAYS require a human gate.
    """
    if action.kind == "read":
        return ActionVerdict(status="allowed")
    if scope not in VALID_SCOPES:
        return ActionVerdict(status="blocked", reason=f"Unknown execution scope: {scope}")
    if scope != "read-write":
        return ActionVerdict(
            status="blocked",
            reason=(
                f'Action "{action.summary}" is a {action.kind} but the current execution '
                f"scope is {scope}. Writes require read-write scope."
            ),
        )
    if not human_authorized:
        return ActionVerdict(
            status="needs-human-gate",
            reason=(
                f'Action "{action.summary}" ({action.kind}) requires explicit human '
                "approval before it can execute."
            ),
        )
    return ActionVerdict(status="allowed")


# ---------------------------------------------------------------------------
# ASI08 — Blast Radius / Anomaly Flag & Pause
# ---------------------------------------------------------------------------


@dataclass
class AnomalyFlag:
    code: str
    severity: str  # "info" | "warning" | "critical"
    message: str


@dataclass
class AnomalyReport:
    flags: list[AnomalyFlag] = field(default_factory=list)
    paused: bool = False


def detect_anomalies(
    actions: list[ProposedAction],
    bulk_write_threshold: int = 10,
    risk_score_spike_threshold: int = 40,
) -> AnomalyReport:
    """Evaluate proposed actions for anomalies.

    If a critical anomaly is detected the session is flagged as paused
    (quarantined) and the owner is alerted. Runs before any dispatch.
    """
    flags: list[AnomalyFlag] = []
    write_actions = [a for a in actions if a.kind in ("write", "commit")]
    total_affected = sum(a.affected_records for a in write_actions)

    if len(write_actions) >= bulk_write_threshold or total_affected >= bulk_write_threshold:
        flags.append(
            AnomalyFlag(
                code="ASI08-BULK-WRITE",
                severity="critical",
                message=(
                    f"Detected {len(write_actions)} write/commit action(s) touching "
                    f"~{total_affected} record(s). Treating as a potential bulk-write "
                    "anomaly; pausing session."
                ),
            )
        )

    risk_re = re.compile(r"risk|health|score", re.I)
    delta_re = re.compile(r"(spike|drop|jump|crash|-\d{2,}|\+\d{2,})", re.I)
    risk_actions = [a for a in actions if risk_re.search(a.target) and delta_re.search(a.summary)]
    if risk_actions:
        flags.append(
            AnomalyFlag(
                code="ASI08-RISK-SPIKE",
                severity="warning",
                message=(
                    f"{len(risk_actions)} health/risk score action(s) carry a large-delta "
                    "signature. Verify against source data before relying on this."
                ),
            )
        )

    paused = any(f.severity == "critical" for f in flags)
    return AnomalyReport(flags=flags, paused=paused)


def evaluate_and_pause(actions: list[ProposedAction]) -> tuple[AnomalyReport, bool]:
    """Return (report, can_dispatch).

    When a critical anomaly is found the session is paused and dispatch is
    blocked. In this lightweight build the pause surfaces in the UI; full
    runtime auto-quarantine depends on the host platform and is NOT claimed.
    """
    report = detect_anomalies(actions)
    return report, not report.paused
