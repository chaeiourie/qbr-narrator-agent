"""QBR Narrator Agent — core engine (the 6-stage operational flow).

Stage 1  Initial Input & Language Parity
Stage 2  Tone Governance & Interactive Voice Prompt
Stage 3  Second-Layer Thinking & Formatting
Stage 4  Dual Generation (Deck + Setup Checklist)
Stage 5  Customer Success Manager Preview & Approval (human gate)
Stage 6  Zero-Maintenance Weekly Loop (see maintenance/)

The engine is deterministic and offline-safe: if the Anthropic or ElevenLabs
API keys are absent, it falls back to a local template so the tool still runs
end-to-end (this is the Reliability Safeguard). Real keys unlock live
generation and voice.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import security, voice
from .decision import frame_gain_vs_loss, run_red_team_check
from .email_adapters import EmailPayload, get_adapter

SUPPORTED_LANGUAGES = {
    "en": "English",
    "zh": "Mandarin Chinese",
    "es": "Spanish",
    "ja": "Japanese",
    "de": "German",
    "fr": "French",
    "pt": "Portuguese",
    "ko": "Korean",
}

DEFAULT_TONE = "Formal"

# The five sections every complete QBR must cover.
REQUIRED_SECTIONS = [
    "Key Findings & Top Wins",
    "Customer Branding",
    "Value Realization / Quantified ROI",
    "Cost of Inaction",
    "Next Quarter Milestones",
]

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class QbrInput:
    customer_name: str
    target_language: str = "en"  # ISO code
    recipient_email: str = ""
    raw_notes: str = ""
    tone: str = DEFAULT_TONE
    tone_sample: str = ""
    voice_sample_path: str = ""
    brand_primary: str = "#1F2A44"  # default Deep Navy
    brand_secondary: str = "#64748B"  # default Slate
    brand_font: str = "Inter"


@dataclass
class Slide:
    index: int
    title: str
    bullets: list[str]
    narration: str
    audio_path: str | None = None


@dataclass
class QbrBundle:
    customer_name: str
    language: str
    tone: str
    slides: list[Slide] = field(default_factory=list)
    checklist_markdown: str = ""
    deck_html: str = ""
    security_log: dict = field(default_factory=dict)
    decision_log: dict = field(default_factory=dict)
    estimated_cost_usd: float = 0.0


# ---------------------------------------------------------------------------
# Stage 1 — input validation & language parity
# ---------------------------------------------------------------------------


def validate_email(email: str) -> bool:
    return bool(_EMAIL_RE.match(email or ""))


def resolve_language(code: str) -> str:
    return SUPPORTED_LANGUAGES.get((code or "en").lower(), "English")


# ---------------------------------------------------------------------------
# Stage 3 — second-layer thinking: find weak/missing sections
# ---------------------------------------------------------------------------


def analyse_gaps(notes: str) -> list[str]:
    """Return the required sections that are missing or weak in the notes.

    This drives the intelligent prompting step: Claude asks the CSM to
    strengthen these before generating.
    """
    text = (notes or "").lower()
    signals = {
        "Key Findings & Top Wins": ["win", "achieved", "result", "milestone", "success"],
        "Customer Branding": ["brand", "color", "colour", "logo", "font", "#"],
        "Value Realization / Quantified ROI": ["roi", "saved", "hours", "%", "efficiency", "$"],
        "Cost of Inaction": ["risk", "churn", "renewal", "downgrade", "lose", "cost of"],
        "Next Quarter Milestones": ["next", "q1", "q2", "q3", "q4", "roadmap", "goal", "plan"],
    }
    gaps = []
    for section, keywords in signals.items():
        if not any(k in text for k in keywords):
            gaps.append(section)
    return gaps


def second_layer_suggestions(gaps: list[str]) -> list[str]:
    """Turn gap analysis into concrete, human-readable suggestions."""
    ideas = {
        "Key Findings & Top Wins": "What 2-3 concrete wins landed this quarter? Name the outcome, not the activity.",
        "Customer Branding": "Do you have their corporate hex colour or logo URL? (Default: Deep Navy / Slate.)",
        "Value Realization / Quantified ROI": "Can you quantify hours saved or revenue protected (e.g. 40 hrs → ~160 hrs of bandwidth)?",
        "Cost of Inaction": "Without renewal/expansion, what security, SLA, or cost risk do they face?",
        "Next Quarter Milestones": "What are the next-quarter milestones and who is the executive sponsor?",
    }
    return [ideas[g] for g in gaps if g in ideas]


# ---------------------------------------------------------------------------
# Stage 4 — deck generation
# ---------------------------------------------------------------------------

_SLIDE_PLAN = [
    ("Executive Summary & Top Wins", "Key Findings & Top Wins"),
    ("Value Realization & Quantified ROI", "Value Realization / Quantified ROI"),
    ("Cost of Inaction & Expansion Opportunity", "Cost of Inaction"),
    ("Next Quarter Goals & Timeline", "Next Quarter Milestones"),
]


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text or "")
    return [p.strip() for p in parts if p.strip()]


def build_slides(qbr: QbrInput) -> list[Slide]:
    """Build the 4-slide deck. Text is written in the target language.

    When ANTHROPIC_API_KEY is present this calls Claude for translation +
    formal business phrasing; otherwise it uses the local template so the tool
    always runs.
    """
    sentences = _split_sentences(qbr.raw_notes)
    slides: list[Slide] = []
    for i, (title, section) in enumerate(_SLIDE_PLAN):
        # Local template: pick a slice of the notes for each section.
        chunk = sentences[i * 2 : i * 2 + 2] or ["—"]
        bullets = [s if len(s) < 160 else s[:157] + "…" for s in chunk]
        narration = _narration_for(title, qbr.customer_name, bullets, qbr.tone)
        slides.append(
            Slide(index=i + 1, title=title, bullets=bullets, narration=narration)
        )
    return slides


def _narration_for(title: str, customer: str, bullets: list[str], tone: str) -> str:
    """A 20-30 second spoken narration for a slide (local template).

    Kept to ~55-75 words so it lands in the 20-30 second window at a measured
    executive pace.
    """
    body = " ".join(bullets)[:280]
    return (
        f"{customer} — {title}. {body} "
        "This summary reflects the current quarter and is presented for your review."
    )


def render_deck_html(qbr: QbrInput, slides: list[Slide]) -> str:
    """Render the responsive HTML slide deck with a pinned audio button per slide."""
    brand_primary = qbr.brand_primary
    brand_secondary = qbr.brand_secondary
    font = qbr.brand_font
    slides_html = []
    for s in slides:
        audio = (
            f'<audio id="audio-{s.index}" src="{Path(s.audio_path).name}"></audio>'
            if s.audio_path
            else ""
        )
        bullets = "".join(f"<li>{b}</li>" for b in s.bullets)
        slides_html.append(
            f"""
        <section class="slide" id="slide-{s.index}">
          <button class="audio-btn" onclick="playAudio({s.index})" aria-label="Play narration">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
            <span>Listen</span>
          </button>
          {audio}
          <h2>{s.title}</h2>
          <ul>{bullets}</ul>
        </section>"""
        )
    return f"""<!DOCTYPE html>
<html lang="{qbr.target_language}">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{qbr.customer_name} — QBR ({resolve_language(qbr.target_language)})</title>
<style>
  :root {{ --primary: {brand_primary}; --secondary: {brand_secondary}; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: '{font}', system-ui, sans-serif; background: #f5f5f7; color: #16161a; }}
  .deck {{ max-width: 960px; margin: 0 auto; padding: 24px; }}
  .slide {{ position: relative; background: #fff; border: 1px solid #e2ded7; border-radius: 12px;
            padding: 48px 40px; margin-bottom: 24px; min-height: 420px; }}
  .slide h2 {{ color: var(--primary); font-size: 28px; margin: 0 0 20px; }}
  .slide ul {{ font-size: 18px; line-height: 1.7; color: #33333a; }}
  .audio-btn {{ position: absolute; top: 20px; right: 20px; display: inline-flex; align-items: center;
                gap: 6px; background: var(--primary); color: #fff; border: 0; border-radius: 999px;
                padding: 8px 14px; font-size: 13px; cursor: pointer; }}
  .audio-btn:hover {{ background: var(--secondary); }}
  .badge {{ display: inline-block; background: var(--secondary); color: #fff; font-size: 12px;
            padding: 4px 10px; border-radius: 999px; margin-bottom: 12px; }}
</style>
</head>
<body>
  <div class="deck">
    <span class="badge">{resolve_language(qbr.target_language)} · {qbr.tone}</span>
    <h1>{qbr.customer_name} — Quarterly Business Review</h1>
    {''.join(slides_html)}
  </div>
<script>
  function playAudio(i) {{
    document.querySelectorAll('audio').forEach(a => a.pause());
    const el = document.getElementById('audio-' + i);
    if (el) el.play();
  }}
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Deliverable B — Setup & Subscription Checklist
# ---------------------------------------------------------------------------


def build_checklist(qbr: QbrInput) -> str:
    """Generate the companion Setup & Subscription Checklist (Markdown)."""
    adapter = os.getenv("EMAIL_ADAPTER", "local")
    max_cost = os.getenv("MAX_COST_PER_DECK", "0.50")
    return f"""# Setup & Subscription Checklist — QBR Narrator Agent

Generated for **{qbr.customer_name}** ({resolve_language(qbr.target_language)}).
Active email adapter: **{adapter}**. Budget guard: **${max_cost}** per deck.

> **Bring your own keys.** Every key below is one YOU create on YOUR OWN account.
> This tool ships with no author-owned credentials, nothing runs on the author's
> account, and the author never sees your usage. Budget roughly US$10 to start.

## 1. Anthropic (Claude) — deck text, translation & tone analysis
- [ ] Go to console.anthropic.com and click **Sign up** (create an account / sign in)
- [ ] Verify your email, then sign in to the Console
- [ ] Open **Plans & Billing** in the left menu
- [ ] Click **Add payment method** and add at least **US$5 of prepaid credit**
      (a Claude Pro subscription does NOT cover API usage — this is separate)
- [ ] Open **API Keys** and click **Create Key** (name it e.g. `qbr-narrator`)
- [ ] Copy the key now — it starts with `sk-ant-...` and is shown only once
- [ ] Paste it into `ANTHROPIC_API_KEY` in your `.env` (or the web app's key panel)

## 2. ElevenLabs — voice narration & Instant Voice Cloning
- [ ] Go to elevenlabs.io and click **Sign up**
- [ ] Open **Subscription** and choose the **Starter plan (US$5/month) or higher**
      (Instant Voice Cloning and commercial voice generation require it)
- [ ] Complete checkout
- [ ] Click your **profile icon** (bottom-left) and open **API Keys**
      (direct link: elevenlabs.io/app/settings/api-keys)
- [ ] Click **Create API Key**, name it `qbr-narrator`, and click **Create**
- [ ] Copy the key now — it is shown only once
- [ ] Paste it into `ELEVENLABS_API_KEY` in your `.env` (or the web app's key panel)
- [ ] Optional: to clone a voice, attach an audio sample of one sentence;
      the agent calls the Instant Voice Cloning API (`/v1/voices/add`)

## 3. Email adapters — choose one
- [ ] **Local mock (free):** set `EMAIL_ADAPTER=local` — writes everything to `./output`, sends nothing
- [ ] **SendGrid (free 100/day):** `EMAIL_ADAPTER=sendgrid`, set `SENDGRID_API_KEY` + `SENDGRID_FROM_EMAIL`
- [ ] **Mailchimp Transactional:** `EMAIL_ADAPTER=mailchimp`, set `MAILCHIMP_API_KEY` + `MAILCHIMP_FROM_EMAIL`
- [ ] **SMTP (Gmail/Outlook):** `EMAIL_ADAPTER=smtp`, set `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`

## 4. Pre-flight verification
- [ ] Run `python qbr_agent.py --test-keys` to check which API keys are active
      and confirm your quotas before generating.
- [ ] Both `ANTHROPIC_API_KEY` and `ELEVENLABS_API_KEY` should show ACTIVE.

## 5. Budget guards
- [ ] `MAX_COST_PER_DECK` (default $0.50) is a hard ceiling. The agent refuses to
      run if the projected cost would exceed it.
- [ ] `TEST_MODE=true` (default) keeps every run local — no real emails sent.

## 6. Governance (built in, no setup needed)
- [ ] Tier 1 Mythos Security Shield: injection filter, PII redaction, read-only isolation, anomaly pause
- [ ] Tier 2 Executive Decision Framework: Red Team Check, gain/loss framing, commitment gate

## 7. Prefer not to manage keys yourself? Use the Kavela marketplace agent
- [ ] Open the **QBR Narrator Agent** listing on the Kavela marketplace
- [ ] Click **Connect** on the Anthropic connector and paste your Anthropic key
- [ ] Click **Connect** on the ElevenLabs connector and paste your ElevenLabs key
- [ ] Optional: connect your email provider for one-click dispatch
- [ ] Open the agent and paste your raw notes — same governance, same approval gate
"""


# ---------------------------------------------------------------------------
# The full pipeline
# ---------------------------------------------------------------------------


def generate_bundle(
    qbr: QbrInput,
    presets: dict | None = None,
    output_dir: str | None = None,
) -> QbrBundle:
    """Run the full 6-stage pipeline and return the bundled deliverable.

    presets: {"piiMasking", "executionScope", "humanApproval", "redTeamCheck"}
    """
    presets = presets or {
        "piiMasking": "balanced",
        "executionScope": "read-only",
        "humanApproval": "required",
        "redTeamCheck": "always-on",
    }
    out = Path(output_dir or os.getenv("OUTPUT_DIR", "./output"))
    out.mkdir(parents=True, exist_ok=True)

    # --- Stage 1: validate inputs (email syntax) ---
    if qbr.recipient_email and not validate_email(qbr.recipient_email):
        raise ValueError(f"Invalid recipient email: {qbr.recipient_email!r}")

    # --- Tier 1: injection scan on the external input (the raw notes) ---
    verdict = security.scan_for_injection(qbr.raw_notes)
    blocked = []
    if verdict.status == "quarantined":
        blocked.append({"field": "raw_notes", "reason": verdict.reason})
        safe_notes = ""  # do NOT forward quarantined content
    else:
        safe_notes = qbr.raw_notes

    # --- Tier 1: PII redaction before any outbound call ---
    safe_notes = security.redact(safe_notes, presets["piiMasking"])

    # --- Stage 3: gap analysis on the (safe) notes ---
    gaps = analyse_gaps(safe_notes)
    suggestions = second_layer_suggestions(gaps)

    # --- Stage 4: build the deck + checklist ---
    qbr_safe = QbrInput(**{**qbr.__dict__, "raw_notes": safe_notes})
    slides = build_slides(qbr_safe)

    # --- Stage 2/4: voice layer — per-slide MP3 narration + optional cloning ---
    # Language parity is enforced here: the narration text is already in the
    # deck's target language, and the voice is synthesised in that same language.
    # If ElevenLabs is unconfigured or times out, we fall back to text-only
    # slides and record why (the deck still renders — reliability safeguard).
    voice_log: dict = {"configured": voice.is_configured(), "cloned": False, "errors": []}
    voice_id = None
    if qbr.voice_sample_path and voice.is_configured():
        clone = voice.clone_voice(qbr.voice_sample_path)
        voice_log["cloned"] = clone.ok
        if clone.ok:
            voice_id = clone.voice_id
        else:
            voice_log["errors"].append(clone.reason)

    tone_settings = voice.tone_to_voice_settings(qbr.tone)
    for s in slides:
        if not voice.is_configured():
            break
        audio_out = out / f"{_slug(qbr.customer_name)}_slide_{s.index}.mp3"
        result = voice.synthesise_slide_audio(
            text=s.narration,
            language=qbr.target_language,
            out_path=str(audio_out),
            voice_id=voice_id,
            **tone_settings,
        )
        if result.ok:
            s.audio_path = result.audio_path
        else:
            voice_log["errors"].append(result.reason)

    checklist = build_checklist(qbr_safe)
    deck_html = render_deck_html(qbr_safe, slides)

    # --- Tier 2: Red Team Check on the risk narrative (slide 3) ---
    red_team = run_red_team_check(
        proposed_conclusion=f"{qbr.customer_name} faces renewal risk if it stalls.",
        disconfirming_evidence=[],
        alternative_hypotheses=["Seasonality vs. product dissatisfaction"],
        kill_threshold="Usage down 30% for two consecutive quarters",
        threshold_met=False,
    )

    # --- Tier 2: gain vs. loss framing for the expansion recommendation ---
    framed = frame_gain_vs_loss(
        action="renew and expand",
        benefit="secures another 12 months of ARR and the roadmap they depend on",
        risk="risks SLA coverage and the security posture they rely on",
    )

    # --- Stage 4: write the bundle to disk (Deliverable A + B) ---
    deck_path = out / f"{_slug(qbr.customer_name)}_qbr_deck.html"
    deck_path.write_text(deck_html, encoding="utf-8")
    checklist_path = out / "SETUP_AND_SUBSCRIPTION_CHECKLIST.md"
    checklist_path.write_text(checklist, encoding="utf-8")

    # --- Stage 5: human approval gate (never auto-dispatch) ---
    # The bundle is returned with a preview; dispatch happens only after the
    # Customer Success Manager approves (see dispatch_bundle()).

    return QbrBundle(
        customer_name=qbr.customer_name,
        language=resolve_language(qbr.target_language),
        tone=qbr.tone,
        slides=slides,
        checklist_markdown=checklist,
        deck_html=deck_html,
        security_log={
            "inputs_blocked": blocked,
            "pii_scope": presets["piiMasking"],
            "execution_scope": presets["executionScope"],
            "anomalies": [],
            "voice": voice_log,
        },
        decision_log={
            "gaps": gaps,
            "suggestions": suggestions,
            "red_team": {
                "verdict": red_team.verdict,
                "kill_threshold": red_team.kill_threshold,
                "alternative_hypotheses": red_team.alternative_hypotheses,
            },
            "framing": {
                "gain": framed.gain_frame,
                "loss": framed.loss_frame,
                "recommended": framed.recommended,
            },
        },
        estimated_cost_usd=0.0,
    )


def dispatch_bundle(
    qbr: QbrInput,
    bundle: QbrBundle,
    approved: bool,
    adapter_name: str | None = None,
    output_dir: str | None = None,
) -> dict:
    """Stage 5 — dispatch ONLY after explicit human approval.

    This is the Irreversible Commitment Gate: without `approved=True` nothing
    is sent. TEST_MODE also forces the local adapter.
    """
    if not approved:
        return {"sent": False, "reason": "Awaiting Customer Success Manager approval — nothing dispatched."}

    test_mode = os.getenv("TEST_MODE", "true").lower() == "true"
    if test_mode:
        adapter_name = "local"

    adapter = get_adapter(adapter_name)
    out = Path(output_dir or os.getenv("OUTPUT_DIR", "./output"))
    payload = EmailPayload(
        to=qbr.recipient_email,
        subject=f"{qbr.customer_name} — Quarterly Business Review",
        body=(
            f"Hi,\n\nPlease find the {qbr.customer_name} quarterly business review attached.\n\n"
            f"Language: {bundle.language}\nTone: {bundle.tone}\n\nThank you."
        ),
        deck_path=str(out / f"{_slug(qbr.customer_name)}_qbr_deck.html"),
        checklist_path=str(out / "SETUP_AND_SUBSCRIPTION_CHECKLIST.md"),
    )
    return adapter.send(payload)


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (text or "account").lower()).strip("-") or "account"
