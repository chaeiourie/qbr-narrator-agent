# Release — QBR Narrator Agent

**Released:** 2026-09-26
**Status:** PUBLIC
**Repo:** https://github.com/chaeiourie/qbr-narrator-agent
**Website page:** https://hicherietan.com/tools/qbr-narrator-agent

---

## What shipped

A lightweight, non-technical agent that turns raw account notes into a **translated QBR slide deck with per-slide voice narration**, plus a companion **setup & subscription checklist**. Built for **Customer Success Managers**.

### Feature set
- **6-stage pipeline** — input & language parity, tone governance, second-layer thinking, dual generation, Customer Success Manager preview & approval, zero-maintenance weekly loop.
- **Deliverable A — Interactive QBR Deck:** responsive 4-slide deck, fully translated, with a "Listen" audio button pinned to every slide playing that slide's native-language narration.
- **Deliverable B — Setup & Subscription Checklist:** exact tiers, API quotas, and step-by-step setup for Claude, ElevenLabs and the email provider.
- **Bring Your Own Keys:** the tool never uses the author's keys and never asks for a password. End users paste their own Anthropic + ElevenLabs keys; in the web app they stay in the user's browser only, in the engine they live in a local git-ignored `.env`.
- **Non-technical web app** (React Router v7): form + button, Bring-Your-Own-Keys panel, Connector Dashboard with Connected/Disconnected status, Security & Privacy Presets. No raw JSON, no terminal.
- **CLI engine** (`qbr_agent.py --test-keys / --demo / --serve`) producing the real files.
- **Zero-manual-maintenance loop:** Monday audit workflow + release-on-approval workflow.

### Verification
- `pytest` — **19 passed** (governance + pipeline + voice).
- `python qbr_agent.py --demo` — generates both deliverables; deck renders 4 slides each with a pinned Listen button.

---

## Changes in this revision

1. **Bring Your Own Keys (no owner tokens).** Added a README section, a real BYO-key panel in the web app (keys held only in the user's browser), an updated `.env.example` header, and updated generated checklist. No author-owned credentials exist anywhere in the repo; the GitHub Actions workflows use `${{ secrets.* }}` placeholders only.
2. **CSM terminology.** Every "account manager" reference replaced with "Customer Success Manager" across the README, engine, CLI, web app, and website.
3. **Detailed setup guide.** Added a full step-by-step Claude + ElevenLabs walkthrough (accounts, plans, prepaid credit, API keys, verification) to the README and the generated checklist.
4. **Kavela marketplace option.** Added "Option C" — the same workflow packaged as a Kavela marketplace agent, where users connect their own accounts through a secure connector vault instead of managing key files.
5. **Website.** hicherietan.com now publishes **only** the QBR Narrator Agent.

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
- **Red Team Check** — tests disconfirming evidence and alternative hypotheses before presenting a risk narrative.
- **Irreversible Commitment Gate** — any action that commits resources, changes terms, or dispatches to a customer is gated behind explicit human approval.
- **Gain vs. Loss framing** — recommendations evaluated in both frames; the more persuasive frame is surfaced.

### Honesty rule
The README states the architecture the tool is actually built on. Controls are real code modules, not marketing claims. The anomaly flag-and-pause behaviour is implemented; full runtime auto-quarantine depends on the host platform — stated plainly, not overclaimed.

---

## Integration surface (scoped against the CS Tool Registry)

| Tool | Status | Auth | Config keys |
|------|--------|------|-------------|
| Anthropic Claude | Integrated | API key (user's own) | `ANTHROPIC_API_KEY` |
| ElevenLabs | Integrated | API key (user's own) | `ELEVENLABS_API_KEY` |
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

- [x] **GitHub** — `chaeiourie/qbr-narrator-agent` public; latest commit pushed.
- [x] **Website** — hicherietan.com publishes only the QBR Narrator Agent.
- [x] **LinkedIn** — copy-ready draft in `LINKEDIN.md` for the owner to post.
