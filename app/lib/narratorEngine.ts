/**
 * QBR Narrator Agent — browser-side engine (TS mirror of engine/qbr_engine.py).
 *
 * The web UI uses this to show a live, non-technical preview of the bundle
 * (deck slides + narration text + checklist). The authoritative generation
 * (real HTML deck, MP3 narration, PDF/Markdown checklist) runs in the Python
 * engine — this mirror keeps the UX instant and offline.
 */

export const SUPPORTED_LANGUAGES: Record<string, string> = {
  en: "English",
  zh: "Mandarin Chinese",
  es: "Spanish",
  ja: "Japanese",
  de: "German",
  fr: "French",
  pt: "Portuguese",
  ko: "Korean",
};

export const DEFAULT_TONE = "Formal";

export const REQUIRED_SECTIONS = [
  "Key Findings & Top Wins",
  "Customer Branding",
  "Value Realization / Quantified ROI",
  "Cost of Inaction",
  "Next Quarter Milestones",
];

export interface Slide {
  index: number;
  title: string;
  bullets: string[];
  narration: string;
}

export function resolveLanguage(code: string): string {
  return SUPPORTED_LANGUAGES[(code || "en").toLowerCase()] ?? "English";
}

const SIGNALS: Record<string, string[]> = {
  "Key Findings & Top Wins": ["win", "achieved", "result", "milestone", "success"],
  "Customer Branding": ["brand", "color", "colour", "logo", "font", "#"],
  "Value Realization / Quantified ROI": ["roi", "saved", "hours", "%", "efficiency", "$"],
  "Cost of Inaction": ["risk", "churn", "renewal", "downgrade", "lose", "cost of"],
  "Next Quarter Milestones": ["next", "q1", "q2", "q3", "q4", "roadmap", "goal", "plan"],
};

export function analyseGaps(notes: string): string[] {
  const text = (notes || "").toLowerCase();
  return Object.entries(SIGNALS)
    .filter(([, keywords]) => !keywords.some((k) => text.includes(k)))
    .map(([section]) => section);
}

const IDEAS: Record<string, string> = {
  "Key Findings & Top Wins":
    "What 2-3 concrete wins landed this quarter? Name the outcome, not the activity.",
  "Customer Branding":
    "Do you have their corporate hex colour or logo URL? (Default: Deep Navy / Slate.)",
  "Value Realization / Quantified ROI":
    "Can you quantify hours saved or revenue protected (e.g. 40 hrs → ~160 hrs of bandwidth)?",
  "Cost of Inaction":
    "Without renewal/expansion, what security, SLA, or cost risk do they face?",
  "Next Quarter Milestones":
    "What are the next-quarter milestones and who is the executive sponsor?",
};

export function secondLayerSuggestions(gaps: string[]): string[] {
  return gaps.map((g) => IDEAS[g]).filter(Boolean);
}

const SLIDE_PLAN = [
  "Executive Summary & Top Wins",
  "Value Realization & Quantified ROI",
  "Cost of Inaction & Expansion Opportunity",
  "Next Quarter Goals & Timeline",
];

function splitSentences(text: string): string[] {
  return (text || "")
    .split(/(?<=[.!?])\s+|\n+/)
    .map((s) => s.trim())
    .filter(Boolean);
}

export function buildSlides(input: {
  customerName: string;
  notes: string;
  tone: string;
}): Slide[] {
  const sentences = splitSentences(input.notes);
  return SLIDE_PLAN.map((title, i) => {
    const chunk = sentences.slice(i * 2, i * 2 + 2);
    const bullets = (chunk.length ? chunk : ["—"]).map((s) =>
      s.length < 160 ? s : s.slice(0, 157) + "…",
    );
    const body = bullets.join(" ").slice(0, 280);
    return {
      index: i + 1,
      title,
      bullets,
      narration: `${input.customerName} — ${title}. ${body} This summary reflects the current quarter and is presented for your review.`,
    };
  });
}

export function buildChecklist(input: {
  customerName: string;
  language: string;
}): string {
  return `Setup & Subscription Checklist — QBR Narrator Agent

Generated for ${input.customerName} (${resolveLanguage(input.language)}).

1. Anthropic (Claude) — deck text, translation & tone analysis
   [ ] Create an account at console.anthropic.com
   [ ] Add Build Tier 1 prepaid API credit ($5 minimum)
   [ ] This needs an API key, NOT a Claude Pro web subscription
   [ ] Copy the key into ANTHROPIC_API_KEY in your .env

2. ElevenLabs — voice narration & Instant Voice Cloning
   [ ] Create an account at elevenlabs.io
   [ ] Subscribe to the Starter plan ($5/mo) or higher
   [ ] Copy your key into ELEVENLABS_API_KEY in your .env
   [ ] Optional: attach an audio sample to clone a voice

3. Email adapters — choose one
   [ ] Local mock (free): EMAIL_ADAPTER=local
   [ ] SendGrid (free 100/day): EMAIL_ADAPTER=sendgrid
   [ ] Mailchimp Transactional: EMAIL_ADAPTER=mailchimp
   [ ] SMTP (Gmail/Outlook): EMAIL_ADAPTER=smtp

4. Pre-flight verification
   [ ] Run: python qbr_agent.py --test-keys

5. Budget guards
   [ ] MAX_COST_PER_DECK (default $0.50) is a hard ceiling
   [ ] TEST_MODE=true (default) keeps every run local

6. Governance (built in, no setup needed)
   [ ] Tier 1 Mythos Security Shield
   [ ] Tier 2 Executive Decision Framework`;
}
