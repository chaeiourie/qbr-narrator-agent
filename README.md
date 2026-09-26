# QBR Narrator Agent — Mythos-Ready CS Automation

Turn raw account notes into a **translated QBR slide deck with pinned voice narration** — plus a companion **setup & subscription checklist** — in minutes, not days.

> **Brand palette:** Built in the Cherie Tj brand system — deep plum `#221521`, brand purple `#734E71`, soft lilac `#F3EAF3`, teal `#66A2A8`, coral `#DC5F6C`, olive `#8B905F`.

Account review prep eats 12+ hours per account: pulling data, writing the narrative, translating it for a global stakeholder, and recording a voiceover that matches. QBR Narrator Agent turns that into one bundled deliverable — a themed deck with a "Listen" button pinned to every slide, and a checklist that spells out exactly what you need to run it yourself.

This is a lightweight agent you run on your **own** computer: a web app with a form and a button, plus a Python engine that produces the real files. Setup is copy-paste — no coding required (see **How to Run It** below). It is built on a **Dual-Layer Enterprise Governance Engine** so the automation is secure by default and the human stays in charge of judgment and commitments.

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
5. **Customer Success Manager Preview & Approval** — nothing is dispatched until the Customer Success Manager approves.
6. **Zero-Maintenance Weekly Loop** — an autonomous Monday audit scans for updates and emails you a 1-click approval.

## Bring Your Own Keys (important)

**This tool never uses the author's API keys, and it never asks you for a password.** You bring your own Anthropic and ElevenLabs keys, and they stay yours.

- **No shared tokens.** There are no author-owned credentials baked into this repo or the web app. Every key is one *you* create on *your* account. There is no hosted instance run by the author.
- **Your keys, your account, your spend.** Generation is billed to your own Anthropic and ElevenLabs accounts. The author pays nothing on your behalf and cannot see your usage.
- **Where your keys live.** In the web app you paste your keys into the **Bring your own keys** panel; they are held only in your browser session (in-memory / local storage on your own device) and are sent *directly* to Anthropic and ElevenLabs — never to the author, never to any third-party server.
- **In the Python engine** your keys live in a local `.env` file on your own machine. That file is git-ignored and is never committed.
- **Nothing is shared between users.** Each CSM runs their own copy with their own keys.

> **No keys? It still runs.** Without the two AI keys the engine runs end-to-end in **local-template mode** — the deck and checklist still generate; only the live AI text and voice are skipped. Add keys when you are ready.

## How to Run It (on your own computer)

> **There is no hosted version of this app, and there never will be.** You run this codebase on **your own computer**, with **your own keys**, on **your own data**. Nothing runs on the author's machine or account. This is deliberate: it means **you** stay in full control of any customer data and any AI calls. See **"Who is responsible for what"** below.

You do **not** need to be a developer. Below are copy-paste steps for a **MacBook** and for **Windows**. Give yourself about 15 minutes the first time.

### What you need first

- A computer (Mac or Windows) with an internet connection.
- **Node.js 20 or newer** (for the web app) and/or **Python 3.11 or newer** (for the engine). Install links are in the steps below.
- Your own **Anthropic** and **ElevenLabs** API keys — see the step-by-step guide further down.

### Step 1 — Download the code

You have two easy options — pick one:

- **Option 1 (no tools needed):** On the GitHub page, click the green **Code** button, then **Download ZIP**. Unzip the folder somewhere easy to find (for example your **Documents** folder). You will get a folder called `qbr-narrator-agent`.
- **Option 2 (if you have Git):** In a terminal, run `git clone https://github.com/chaeiourie/qbr-narrator-agent.git`.

### Step 2 — Open a terminal in that folder

A "terminal" is just a window where you type commands. You will only type the exact lines shown.

- **MacBook:** Open **Terminal** (press `Cmd + Space`, type `Terminal`, press Enter). Then type `cd ` (with a space), drag the `qbr-narrator-agent` folder from Finder into the Terminal window, and press Enter. The folder path fills in automatically.
- **Windows:** Open the `qbr-narrator-agent` folder in File Explorer. Click the address bar, type `cmd`, and press Enter. A black Command Prompt window opens already pointed at the folder.

### Step 3 — Run the app (choose ONE of the two below)

#### 3A — The web app (a form and a button in your browser)

1. Install **Node.js**: go to **nodejs.org**, download the **LTS** version, and run the installer (click Next through it). Close and reopen your terminal afterwards.
2. In the terminal, type this and press Enter:
   ```
   npm install
   ```
   This downloads the app's building blocks. It takes a minute or two the first time.
3. Then type this and press Enter:
   ```
   npm run dev
   ```
4. The terminal will print a line like `Local: http://localhost:5173/`. Open that address in your browser (Chrome, Safari, or Edge). **That is the app** — the form, the **Bring your own keys** panel, and the **Connect your CS tools** dashboard.
5. When you are finished, click back in the terminal and press `Ctrl + C` to stop the app.

#### 3B — The Python engine (produces the real deck and checklist files)

1. Install **Python 3.11+**: go to **python.org/downloads**, download the installer, and run it. **On Windows, tick the box "Add Python to PATH"** on the first screen — this matters.
2. In the terminal, type this and press Enter:
   ```
   pip install -r requirements.txt
   ```
3. Make your keys file: copy `.env.example` to a new file named `.env` in the same folder, then open `.env` in any text editor (Notepad on Windows, TextEdit on Mac) and paste in **your own** keys. Save it. (`.env` is git-ignored — it is never uploaded anywhere.)
4. Check your keys are working:
   ```
   python qbr_agent.py --test-keys
   ```
   You should see `[ACTIVE]` next to the keys you filled in.
5. Generate a sample bundle (writes the deck and checklist into the `output` folder):
   ```
   python qbr_agent.py --demo
   ```

**Budget guard:** `MAX_COST_PER_DECK` (default `$0.50`) is a hard ceiling — the agent refuses to run if the projected cost would exceed it. **`TEST_MODE=true`** (the default) keeps every run local, so you can explore safely.

> Without the two AI keys the engine still runs end-to-end in **local-template mode** (deck + checklist generate; audio is skipped). Add your keys to unlock live generation and voice.

---

## Who is responsible for what

This project is published as **open-source code for you to run yourself**. It is **not** a hosted service, and the author does **not** operate it on anyone's behalf.

- **You run it, you own it.** The author provides the code under the MIT licence and nothing more. The author does not receive, store, or process your data or your customers' data, and has no access to your keys, your accounts, or your outputs.
- **Your keys, your accounts.** You bring your own Anthropic and ElevenLabs keys and pay for your own usage. The author pays nothing on your behalf.
- **Your data, your responsibility.** Any customer notes, PII, or confidential information you put into the tool stays on **your** machine and goes only to the providers **you** have configured. You are responsible for having the right to use that data and for complying with your own company's policies and applicable privacy law (for example GDPR, CCPA).
- **No warranty.** The code is provided "as is", without warranty of any kind. You are responsible for reviewing every generated deck, translation, and narration before it reaches a customer. See the [LICENSE](LICENSE).
- **No liability.** To the fullest extent permitted by law, the author accepts no liability for any loss, claim, or damage arising from your use of this code, including any data exposure, misuse, or downstream consequence.

In short: **the code is yours to run; the responsibility for how you run it is yours too.**

---

## Step-by-step setup: Claude and ElevenLabs

This is the full walkthrough for both keys. No prior experience needed — just a web browser and a card for the two small subscriptions. Budget roughly **US$10** to get started ($5 Anthropic credit + $5/month ElevenLabs).

### Part 1 — Anthropic Claude (the text, translation and tone)

Claude writes and translates your slide text and reads your tone sample. You need an **API key** — this is different from a Claude Pro chat subscription.

1. Go to **console.anthropic.com** and click **Sign up**. Create an account with your email (or sign in if you already have one).
2. Verify your email, then sign in to the Console.
3. In the left menu, open **Plans & Billing** (sometimes shown as **Billing**).
4. Click **Add payment method** and enter a card. Anthropic's API is **prepaid** — add at least **US$5** of credit. (A Claude Pro subscription does **not** cover API usage; this is a separate, pay-as-you-go balance.)
5. In the left menu, open **API Keys** and click **Create Key**. Name it something like `qbr-narrator`.
6. **Copy the key now** — it starts with `sk-ant-...`. Anthropic shows it only once. Paste it somewhere safe for a moment (you will paste it into the tool next).
7. Paste it into your `.env` file as `ANTHROPIC_API_KEY=sk-ant-...` (for the Python engine), or into the **Bring your own keys** panel in the web app.

**Rough cost:** a full deck + translation is a few cents. The `MAX_COST_PER_DECK` guard stops any run that would exceed your ceiling.

### Part 2 — ElevenLabs (the per-slide voice narration)

ElevenLabs turns each slide's narration into a spoken MP3 in the deck's language.

1. Go to **elevenlabs.io** and click **Sign up**. Create an account with your email or Google.
2. Open **Subscription** (or **Pricing**) in the left menu and choose the **Starter** plan (**US$5/month**). Starter or higher is required for **Instant Voice Cloning** and commercial voice generation — the free tier will not unlock these.
3. Complete checkout.
4. In the left menu, click your **profile icon** (bottom-left) and open **API Keys** (direct link: **elevenlabs.io/app/settings/api-keys**).
5. Click **Create API Key**, name it `qbr-narrator`, and click **Create**.
6. **Copy the key now** — it is shown only once. Paste it somewhere safe for a moment.
7. Paste it into your `.env` file as `ELEVENLABS_API_KEY=...` (for the Python engine), or into the **Bring your own keys** panel in the web app.
8. *(Optional)* If you want the narration in a specific voice, copy that voice's **Voice ID** from **Voices → your voice → ID** and set `ELEVENLABS_VOICE_ID=...`. Leave it blank to use the built-in formal executive narrator.

### Part 3 — Email (optional, for dispatch)

Only needed if you want the agent to email the finished deck. Pick one:

- **Local mock (free, default):** `EMAIL_ADAPTER=local` — writes everything to `./output`, sends nothing. Best for your first run.
- **SendGrid (free tier, 100 emails/day):** `EMAIL_ADAPTER=sendgrid` + `SENDGRID_API_KEY` + `SENDGRID_FROM_EMAIL`.
- **Mailchimp Transactional:** `EMAIL_ADAPTER=mailchimp` + `MAILCHIMP_API_KEY` + `MAILCHIMP_FROM_EMAIL`.
- **SMTP (Gmail / Outlook):** `EMAIL_ADAPTER=smtp` + `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`.

### Part 4 — Verify your keys

Run the pre-flight check to confirm both keys are active before you generate:

```
python qbr_agent.py --test-keys
```

You should see `[ACTIVE]` next to `ANTHROPIC_API_KEY` and `ELEVENLABS_API_KEY`. If a key shows `missing`, re-copy it (a trailing space is the usual culprit).

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
