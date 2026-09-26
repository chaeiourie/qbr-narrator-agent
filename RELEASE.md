# Release — QBR Narrator Agent

**Released:** 2026-09-26
**Status:** PUBLIC
**Repo:** https://github.com/chaeiourie/qbr-narrator-agent
**Website page:** https://hicherietan.com/tools/qbr-narrator-agent

---

## What shipped

A lightweight, non-technical agent that turns raw account notes into a **translated QBR slide deck with per-slide voice narration**, plus a companion **setup & subscription checklist**.

### Feature set
- **6-stage pipeline** — input & language parity, tone governance, second-layer thinking, dual generation, manager preview & approval, zero-maintenance weekly loop.
- **Deliverable A — Interactive QBR Deck:** responsive 4-slide deck, fully translated, with a "Listen" audio button pinned to every slide playing that slide's native-language narration.
- **Deliverable B — Setup & Subscription Checklist:** exact tiers, API quotas, and setup steps for Claude, ElevenLabs and the email provider.
- **Non-technical web app** (React Router v7): form + button, Connector Dashboard with Connected/Disconnected status, Security & Privacy Presets. No raw JSON, no terminal.
- **CLI engine** (`qbr_agent.py --test-keys / --demo / --serve`) producing the real files.
- **Zero-manual-maintenance loop:** Monday audit workflow + release-on-approval workflow.

### Verification
- `pytest` — **19 passed** (governance + pipeline + voice).
- `python qbr_agent.py --demo` — generates both deliverables; deck renders 4 slides each with a pinned Listen button.
- `npm run build` — web app builds clean.

---

## Security review — Mythos Governance Standard (embedded as real code)

### Tier 1 — Mythos Security Shield (`engine/security.py`)
| Control | Standard | Implementation |
|---------|----------|----------------|
| Prompt-injection filter | ASI01 / LLM01 | Scans all external inputs for instruction-override, persona-hijack and exfiltration patterns; quarantines suspicious input before it reaches the drafting engine. |
| PII & secret redaction | LLM02 / LLM05 | Masks emails, phones, SSNs, API keys, bearer tokens and card-like numbers in local memory before any outbound call. Scopes: strict / balanced / off. |
| Read-only supply-chain isolation | ASI04 | Reads always allowed; **writes blocked** unless scope is `read-write` AND a human gate authorizes the specific action; **commits always require a human gate**. |
| Anomaly flag & pause | ASI08 | Bulk writes, abnormal risk-score spikes or unexpected write volume flag and pause the session for review. |

### Tier 2 — Executive Decision Framework (`engine/decision.py`)
- **Human-in-the-loop responsibility** — machine handles calculation & drafting; the CSM retains judgment & sign-off. The agent never dispatches to a customer or makes an irreversible commitment autonomously.
- **Red Team Check** — tests disconfirming evidence and alternative hypotheses before presenting a risk narrative; if the pre-registered kill threshold is not met, the analysis is flagged for review rather than presented one-sided.
- **Irreversible Commitment Gate** — any action that commits resources, changes terms, or dispatches to a customer is gated behind explicit human approval.
- **Gain vs. Loss framing** — recommendations evaluated in both frames; the more persuasive frame is surfaced.

### Honesty rule
The README states the architecture the tool is actually built on. Controls are real code modules, not marketing claims. The anomaly flag-and-pause behaviour is implemented; full runtime auto-quarantine depends on the host platform — this is stated plainly, not overclaimed.

---

## Integration surface (scoped against the CS Tool Registry)

| Tool | Status | Auth | Config keys |
|------|--------|------|-------------|
| Anthropic Claude | Integrated | API key | `ANTHROPIC_API_KEY` |
| ElevenLabs | Integrated | API key | `ELEVENLABS_API_KEY` |
| Gainsight | Integrated | API key | `GAINSIGHT_API_KEY` |
| Salesforce | Integrated | OAuth2 / JWT | `SALESFORCE_INSTANCE_URL`, `SALESFORCE_CLIENT_ID`, `SALESFORCE_CLIENT_SECRET` |
| Zendesk | Integrated | API token | `ZENDESK_SUBDOMAIN`, `ZENDESK_API_TOKEN` |
| HubSpot | Integrated | API key / OAuth2 | `HUBSPOT_API_KEY` |
| Totango | Integrated | API key | `TOTANGO_API_KEY` |
| ChurnZero | Integrated | API key | `CHURNZERO_API_KEY` |
| Gong | **watch** | OAuth2 | `GONG_CLIENT_ID`, `GONG_CLIENT_SECRET` |

**Honest status:** Gong is marked `watch` — it needs a Gong OAuth2 app that is not a stable no-code path for this lightweight build, so it is listed but **not wired as a working connector**. The connector dashboard shows it as "Not available." All integrations are read-only by default (ASI04).

---

## Publishing pipeline — executed

- [x] **GitHub** — `chaeiourie/qbr-narrator-agent` toggled **private → public**. Confirmed `"visibility":"public"`.
- [x] **Website** — QBR Narrator Agent added to hicherietan.com as the first "Shipped" card + a full tool page (problem, why it matters, capabilities, setup, GitHub links).
- [x] **LinkedIn** — copy-ready draft handed to the owner (personal-profile posting requires an approved LinkedIn OAuth app; the owner posts it).
