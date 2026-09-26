"""Executive Decision Framework (Tier 2).

The machine handles Calculation & Drafting; the human retains Judgment &
Decision sign-off. This module implements:
  - Red Team Check (falsification / anti-confirmation-bias)
  - Gain vs. Loss framing audit (loss aversion)
  - Irreversible Resource Commitment Gate
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Red Team Check (anti-confirmation bias)
# ---------------------------------------------------------------------------


@dataclass
class RedTeamCheck:
    proposed_conclusion: str
    disconfirming_evidence: list[str] = field(default_factory=list)
    alternative_hypotheses: list[str] = field(default_factory=list)
    kill_threshold: str = ""
    threshold_met: bool = False
    verdict: str = "pass"  # "pass" | "flag-for-review"


def run_red_team_check(
    proposed_conclusion: str,
    disconfirming_evidence: list[str],
    alternative_hypotheses: list[str],
    kill_threshold: str,
    threshold_met: bool,
) -> RedTeamCheck:
    """Run a Red Team Check on a proposed risk analysis.

    The tool will not present a one-sided "account is at risk" narrative. If the
    kill threshold is not met, or disconfirming evidence is strong, the analysis
    is flagged for review.
    """
    strong_disconfirming = len(disconfirming_evidence) >= 2
    verdict = "flag-for-review" if (strong_disconfirming or not threshold_met) else "pass"
    return RedTeamCheck(
        proposed_conclusion=proposed_conclusion,
        disconfirming_evidence=list(disconfirming_evidence),
        alternative_hypotheses=list(alternative_hypotheses),
        kill_threshold=kill_threshold,
        threshold_met=threshold_met,
        verdict=verdict,
    )


# ---------------------------------------------------------------------------
# Gain vs. Loss framing (loss aversion)
# ---------------------------------------------------------------------------


@dataclass
class FramedMessage:
    gain_frame: str
    loss_frame: str
    recommended: str  # "gain" | "loss"
    rationale: str


def frame_gain_vs_loss(action: str, benefit: str, risk: str) -> FramedMessage:
    """Present a recommendation in BOTH a gain frame and a loss frame.

    Enterprises are often more responsive to loss-prevention framing (loss
    aversion); the tool surfaces both and notes which is likely more persuasive.
    """
    return FramedMessage(
        gain_frame=f"Choosing to {action} {benefit}.",
        loss_frame=f"Failing to {action} {risk}.",
        recommended="loss",
        rationale=(
            "For enterprise renewal decisions, loss-prevention framing is generally "
            "more persuasive because decision-makers are loss-averse. Present the loss "
            "frame first, then the gain frame."
        ),
    )


# ---------------------------------------------------------------------------
# Irreversible Resource Commitment Gate
# ---------------------------------------------------------------------------

VALID_COMMITMENT_STATUS = ("draft", "awaiting-approval", "approved", "rejected")


@dataclass
class Commitment:
    id: str
    description: str
    resource: str
    arr_impact: float
    status: str = "draft"


def require_commitment_approval(commitment: Commitment) -> Commitment:
    """Any action that commits resources, changes terms, or alters an engagement
    model is gated behind explicit human approval. The tool surfaces the proposed
    commitment and WAITS; it never auto-approves."""
    if commitment.status != "approved":
        commitment.status = "awaiting-approval"
    return commitment


def approve_commitment(commitment: Commitment) -> Commitment:
    """The single point where a drafted commitment becomes actionable.

    Only a human may call this (via the approval gate)."""
    commitment.status = "approved"
    return commitment
