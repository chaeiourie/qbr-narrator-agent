# QBR Narrator Agent — Mythos-Ready CS Automation

Turn raw account notes into a **translated QBR slide deck with pinned voice narration** — plus a companion **setup & subscription checklist** — in minutes, not days.

> **Brand palette:** Built in the Cherie Tj brand system — deep plum `#221521`, brand purple `#734E71`, soft lilac `#F3EAF3`, teal `#66A2A8`, coral `#DC5F6C`, olive `#8B905F`.

Account review prep eats 12+ hours per account: pulling data, writing the narrative, translating it for a global stakeholder, and recording a voiceover that matches. QBR Narrator Agent turns that into one bundled deliverable — a themed deck with a "Listen" button pinned to every slide, and a checklist that spells out exactly what you need to run it yourself.

This is a lightweight, non-technical agent: a runnable web app with a form and a button, plus a Python engine that produces the real files. No code, no terminal, no setup beyond pasting your notes. It is built on a **Dual-Layer Enterprise Governance Engine** so the automation is secure by default and the human stays in charge of judgment and commitments.

---

## Why This Beats Generic Market Agents

Generic AI agents operate as simple "prompt-in, text-out" wrappers, leaving teams vulnerable to hallucinations, data leakage, and unaligned decision-making. QBR Narrator Agent is built on a **Dual-Layer Enterprise Governance Engine**:

### 1. Mythos Security Shield
- **Injection Isolation (ASI01/LLM01):** Hardened against direct and indirect prompt injection. Every external input (your raw notes, ticket summaries, transcript excerpts) is filtered at the boundary before it reaches the drafting engine.
- **Agentic Supply Chain Safety (ASI04):** Restricted tool agency with strict **read-only** boundaries by default. No connector writes to a downstream system (Gainsight, Salesforce, Zendesk) unless a human-in-the-loop gate explicitly authorizes a specific write.
- **Zero-Trust Data Protection (LLM02/LLM05):** Automatic local stripping of sensitive enterprise PII and contract specifics before any outbound call.

### 2. Applied Decision Framework
- **Human-in-the-Loop Responsibility:** The machine handles high-speed **Calculation & Drafting**; the human CSM retains **Judgment & Decision** sign-off. The agent never dispatches to a customer or makes an irreversible commitment autonomously.
- **Red-Teamed Insights:** Automatically tests disconfirming evidence and alternative hypotheses to eliminate confirmation bias in the "account is at risk" narrative.
- **Risk-Adjusted Execution:** Evaluates ARR impact and executive risk tolerance before generating outputs, presented in both gain and loss frames.

> **Honesty rule:** This README describes the architecture the tool is actually built on. The security controls are real code modules (see `engine/security.py` and `engine/decision.py`), not marketing claims. We do not claim platform-enforced guarantees the shipped code cannot hold — e.g. the anomaly **flag-and-pause** behavior is implemented, but full runtime auto-quarantine depends on the host platform.

---

## Value Proposition

Account review prep eats 12+ hours per account pulling data, hand-building slides, translating them, and recording a voiceover. QBR Narrator Agent turns your raw notes into a complete, ready-to-review bundle — a translated deck with per-slide narration and a setup checklist — so you spend your time on the conversation, not the assembly.

## What & Why

**What it does** — You provide the customer name, target language, recipient email, and raw notes. The agent runs a 6-stage flow and returns a **two-part bundle**:

- **Deliverable A — Interactive QBR Deck:** a responsive 4-slide presentation, 100% translated into your chosen language with formal business phrasing, styled in the customer's brand colors, with an audio icon pinned to each slide that plays that slide's native-language narration.
- **Deliverable B — Setup & Subscription Checklist:** an accompanying checklist (companion tab + exportable PDF/Markdown) that spells out the exact subscription tiers, API quotas, and setup steps for Claude, ElevenLabs, and your email provider.

**Why it matters** — Reclaims hours every account, removes the manual translation-and-voiceover work, and gives non-technical CSMs a governance-baked starting point they can trust. The machine drafts; you decide.

### The 6-stage flow

1. **Initial Input & Language Parity** — customer, target language, recipient email, raw notes. The spoken narration always matches the deck's language.
2. **Tone Governance** — defaults to Formal (Enterprise Executive). Switch the tone, paste a sample sentence, or attach an audio sample to trigger ElevenLabs Instant Voice Cloning.
3. **Second-Layer Thinking** — the engine checks your notes against the five required QBR sections and suggests 2-3 concrete ways to strengthen the weak ones before generating.
4. **Dual Generation** — the deck and the setup checklist are produced together as one bundle.
5. **Manager Preview & Approval** — nothing is dispatched until the account manager approves.
6. **Zero-Maintenance Weekly Loop** — an autonomous Monday audit scans for updates and emails you a 1-click approval.

## How to Deploy

Assume you have never used a terminal. There are two ways to run this.

### Option A — the web app (no terminal)

1. Open the app — a single page with a form and a button.
2. Fill in the customer name, target language, recipient email, and paste your raw notes.
3. Press **Generate deck + checklist**. Review the deck slides (each with a "Listen" button) and the checklist tab.
4. Press **Approve & queue dispatch** — only then does anything go out.

### Option B — the Python engine (produces the real files)

1. Install Python 3.11+ and, in a terminal, run `pip install -r requirements.txt`.
2. Copy `.env.example` to `.env` and fill in the keys you have (see the checklist below).
3. Run the pre-flight check: `python qbr_agent.py --test-keys` — this tells you which keys are active.
4. Generate a sample bundle: `python qbr_agent.py --demo` — writes the HTML deck and the checklist to `./output`.

### The keys you need (and where to get them)

| Key | What it's for | Where to get it |
|-----|---------------|-----------------|
| `ANTHROPIC_API_KEY` | Deck text, translation & tone analysis | console.anthropic.com — needs **Build Tier 1 prepaid credit ($5 min)**, an API key (not a Claude Pro subscription) |
| `ELEVENLABS_API_KEY` | Voice narration & Instant Voice Cloning | elevenlabs.io — requires the **Starter plan ($5/mo) or higher** |
| `EMAIL_ADAPTER` | Which email path to use | `local` (free mock), `sendgrid`, `mailchimp`, or `smtp` |

**Budget guard:** `MAX_COST_PER_DECK` (default `$0.50`) is a hard ceiling — the agent refuses to run if the projected cost would exceed it. **`TEST_MODE=true`** (the default) keeps every run local, so you can explore safely.

> Without the two AI keys the engine still runs end-to-end in **local-template mode** (deck + checklist generate; audio is skipped). Add the keys to unlock live generation and voice.

---

## Integration Surface

QBR Narrator Agent can pull account data from your CS tool stack. Each integration is a **named, swappable module** scoped against the CS Tool Registry, configured through a no-code connector dashboard (Connected/Disconnected status, Configure action, ON/OFF toggle — never raw JSON for the end user).

| Tool | Status | Auth | Config Keys | What It Pulls |
|------|--------|------|-------------|---------------|
| Anthropic Claude | ✅ Integrated | API key | `ANTHROPIC_API_KEY` | Deck text, translation, tone analysis |
| ElevenLabs | ✅ Integrated | API key | `ELEVENLABS_API_KEY` | Per-slide voice narration, voice cloning |
| Gainsight | ✅ Integrated | API key | `GAINSIGHT_API_KEY` | Health scores, usage, account attributes |
| Salesforce | ✅ Integrated | OAuth2 / JWT | `SALESFORCE_INSTANCE_URL`, `SALESFORCE_CLIENT_ID`, `SALESFORCE_CLIENT_SECRET` | MRR, account objects, renewal data |
| Zendesk | ✅ Integrated | API token | `ZENDESK_SUBDOMAIN`, `ZENDESK_API_TOKEN` | Support ticket volume and sentiment |
| HubSpot | ✅ Integrated | API key / OAuth2 | `HUBSPOT_API_KEY` | Company records, tickets, engagement |
| Totango | ✅ Integrated | API key | `TOTANGO_API_KEY` | Customer health and journey data |
| ChurnZero | ✅ Integrated | API key | `CHURNZERO_API_KEY` | Health scores, usage signals, playbook data |
| Gong | 👀 Watch | OAuth2 | `GONG_CLIENT_ID`, `GONG_CLIENT_SECRET` | Call sentiment and meeting signals |

**Honest status:** Gong is marked **`watch`** in the CS Tool Registry. It requires a Gong OAuth2 app that is not a stable no-code path for this lightweight build, so it is listed but **not wired as a working connector**. We do not pretend it works — the connector dashboard shows it as "Not available."

All integrations are **read-only by default** (ASI04). No connector writes to a downstream system without an explicit human authorization gate.

---

## Repo Structure

```
qbr-narrator-agent/
├── README.md
├── LICENSE
├── requirements.txt
├── .env.example                 # Template for all keys (never commit real secrets)
├── integrations.json            # The scoped integration registry (CS Tool Registry bridge)
├── qbr_agent.py                 # CLI: --test-keys, --demo, --serve
├── engine/                      # The Python engine (authoritative generation)
│   ├── qbr_engine.py            # The 6-stage pipeline + deck/checklist builders
│   ├── voice.py                 # ElevenLabs: per-slide MP3 narration + Instant Voice Cloning
│   ├── security.py              # Tier 1 Mythos Security Shield (ASI01/LLM01/LLM02/ASI04/ASI08)
│   ├── decision.py              # Tier 2 Executive Decision Framework
│   ├── integrations.py          # Swappable CS tool integration modules
│   └── email_adapters.py        # Local mock / SendGrid / Mailchimp / SMTP
├── maintenance/                 # Zero-manual-maintenance loop
│   ├── weekly_audit.py          # Monday scan + tests + staging branch + approval email
│   └── on_approval.py           # Merge, tag, publish — only on explicit "Approve"
├── .github/workflows/           # Scheduled audit + release-on-approval workflows
├── tests/                       # pytest suite (governance + pipeline)
└── app/                         # The React Router v7 web UI (non-technical surface)
    ├── routes/home.tsx
    ├── components/narrator/     # Workspace, ConnectorDashboard, SecurityPresetsPanel
    └── lib/                     # Browser-side engine mirror + presets + registry
```

---

## Security & Governance (the real controls)

**Tier 1 — Mythos Security Shield (`engine/security.py`)**
- **Prompt Injection Filter:** scans all external inputs for instruction-override, persona-hijack, and exfiltration patterns before they reach the drafting engine. Quarantines suspicious input. (ASI01/LLM01)
- **PII & Secret Redaction:** masks emails, phones, SSNs, API keys, bearer tokens, and card-like numbers in local memory before any outbound call. Three scopes: strict, balanced, off. (LLM02/LLM05)
- **Read-Only Supply-Chain Isolation:** reads are always allowed; **writes are blocked** unless the scope is `read-write` AND a human gate authorizes the specific action; **commits always require a human gate**. (ASI04)
- **Anomaly Flag & Pause:** bulk writes, abnormal risk-score spikes, or unexpected write volume flag the session and pause it for review. (ASI08)

**Tier 2 — Executive Decision Framework (`engine/decision.py`)**
- **Red Team Check:** before presenting a risk narrative, the tool tests disconfirming evidence and alternative hypotheses. If the pre-registered kill threshold is not met, the analysis is flagged for review — never presented one-sided.
- **Gain vs. Loss Framing:** recommendations are evaluated in both frames (loss aversion) and the more persuasive frame is surfaced.
- **Irreversible Commitment Gate:** any action that commits resources, changes terms, or dispatches to a customer is gated behind explicit human approval.

**Non-technical UX:** all of this is exposed as friendly toggles and selects — **Security & Privacy Presets** and a **Connector Dashboard** — never raw JSON or terminal commands.

---

## Autonomous Upkeep (zero-manual-maintenance)

Set up once, then never update the repo by hand:

1. **Scheduled weekly audit** — every Monday at 09:00 UTC (`.github/workflows/weekly-maintenance.yml`), scanning for new Anthropic/ElevenLabs releases, new community adapters, and security advisories in `requirements.txt`.
2. **Automated upgrade & regression testing** — updates `requirements.txt`, runs `pytest` in dry-run, and prepares a draft release with a `CHANGELOG` on a staging branch.
3. **One-click approval email** — a summary goes to `chaeiourie@gmail.com` with a bulleted changelog, test status, and the line: *"Reply 'Approve' to auto-merge, tag release, and push to GitHub."*
4. **Autonomous release on approval** — on an "Approve" reply, the staging branch merges to `main`, a semantic version tag is bumped, and the release is published with a confirmation email.

**Safety:** the maintenance loop prepares and waits. Nothing merges, tags, or publishes without your explicit "Approve".

---

## What This Does Not Cover

- **Implementation of every CS tool API.** The connectors are scoped and swappable, but each needs your real credentials and your data model. Gong is not wired (see the integration table).
- **Translation quality guarantees.** Live translation runs through Claude; without the key the engine uses a local template. Always review before sending to a customer.
- **Voice cloning consent.** Instant Voice Cloning requires that you have the speaker's permission. You are responsible for consent.
- **Change management.** Introducing agent-augmented processes requires framing and trust. The tool tells the system what to do; you tell your team why.

---

## Engage

- ⭐ **Star** this repo: <https://github.com/chaeiourie/qbr-narrator-agent>
- 🍴 **Fork** it: <https://github.com/chaeiourie/qbr-narrator-agent/fork>
- 💬 **Feedback / issues:** <https://github.com/chaeiourie/qbr-narrator-agent/issues>
- 🔁 **Reshare on LinkedIn:** <https://www.linkedin.com/sharing/share-offsite/?url=https%3A%2F%2Fgithub.com%2Fchaeiourie%2Fqbr-narrator-agent>
- 🌐 **By [Cherie Tj](https://hicherietan.com)** — AI-Native Customer Success & Enablement Leader.

## Licence

[MIT](LICENSE)
