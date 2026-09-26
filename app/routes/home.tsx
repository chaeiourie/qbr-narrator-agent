import type { Route } from "./+types/home";
import { ShieldCheck, Sparkles, Workflow, Rocket, Languages } from "lucide-react";
import { ConnectorDashboard } from "../components/narrator/ConnectorDashboard";
import { NarratorWorkspace } from "../components/narrator/NarratorWorkspace";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "QBR Narrator Agent — Mythos-Ready CS Automation" },
    {
      name: "description",
      content:
        "A secure, non-technical QBR agent that generates a translated slide deck with pinned voice narration plus a setup checklist. The machine drafts, you decide — behind the Mythos Security Shield.",
    },
  ];
}

export default function Home() {
  return (
    <main className="min-h-screen bg-[#FAF8F4] text-[#16161a]">
      {/* Hero */}
      <header className="bg-white">
        <div className="mx-auto max-w-6xl px-6 py-16 text-center">
          <span className="inline-flex items-center gap-1.5 rounded-full bg-[#F3EAF3] px-3 py-1 text-xs font-semibold text-[#734E71]">
            <ShieldCheck className="h-3.5 w-3.5" />
            Mythos-Ready · Dual-Layer Governance
          </span>
          <h1 className="mt-6 text-4xl font-bold tracking-tight text-[#221521] sm:text-5xl">
            QBR Narrator Agent
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-[#46464d]">
            Turn raw notes into a translated slide deck with pinned voice
            narration — plus a setup checklist — in minutes. The machine handles
            the drafting, translation, and audio. You keep judgment, strategy,
            and every commitment.
          </p>
          <p className="mx-auto mt-4 max-w-2xl text-sm text-[#6B6B72]">
            Built for Customer Success Managers. Bring your own Anthropic and
            ElevenLabs keys — they stay in your browser, and nothing runs on
            anyone else's account.
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <a
              href="#workspace"
              className="inline-flex items-center gap-2 rounded-lg bg-[#734E71] px-5 py-2.5 text-sm font-medium text-white hover:bg-[#5e3f5c]"
            >
              <Sparkles className="h-4 w-4" />
              Open the Narrator Workspace
            </a>
            <a
              href="https://vercel.com/new"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 rounded-lg border border-[#E2DED7] bg-white px-5 py-2.5 text-sm font-medium text-[#46464d] hover:bg-[#FAF8F4]"
            >
              <Rocket className="h-4 w-4" />
              Deploy to Vercel
            </a>
          </div>
        </div>
      </header>

      {/* Why it beats generic agents */}
      <section className="mx-auto max-w-6xl px-6 py-10">
        <div className="grid gap-6 md:grid-cols-3">
          <div className="rounded-2xl border border-[#E2DED7] bg-white p-6 shadow-sm">
            <Workflow className="h-6 w-6 text-[#734E71]" />
            <h3 className="mt-3 text-base font-semibold text-[#221521]">
              Injection Isolation (ASI01/LLM01)
            </h3>
            <p className="mt-2 text-sm text-[#46464d]">
              Every external input is scanned for prompt-injection and
              tool-hijacking payloads before it ever reaches the model.
            </p>
          </div>
          <div className="rounded-2xl border border-[#E2DED7] bg-white p-6 shadow-sm">
            <ShieldCheck className="h-6 w-6 text-[#734E71]" />
            <h3 className="mt-3 text-base font-semibold text-[#221521]">
              Zero-Trust Data Protection (LLM02/LLM05)
            </h3>
            <p className="mt-2 text-sm text-[#46464d]">
              Customer PII, tokens, and contract terms are redacted locally
              before any outbound AI call.
            </p>
          </div>
          <div className="rounded-2xl border border-[#E2DED7] bg-white p-6 shadow-sm">
            <Languages className="h-6 w-6 text-[#734E71]" />
            <h3 className="mt-3 text-base font-semibold text-[#221521]">
              Language Parity, Enforced
            </h3>
            <p className="mt-2 text-sm text-[#46464d]">
              The spoken narration always matches the deck's language — English
              deck, English voice; Japanese deck, Japanese voice.
            </p>
          </div>
        </div>
      </section>

      {/* Workspace */}
      <section id="workspace" className="mx-auto max-w-6xl px-6 py-10">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-[#221521]">
            Build your QBR bundle
          </h2>
          <p className="mt-1 text-[#46464d]">
            Enter customer details, tune your security presets, and let the
            engine draft the deck, narration, and checklist.
          </p>
        </div>
        <NarratorWorkspace />
      </section>

      {/* Connectors */}
      <section className="mx-auto max-w-6xl px-6 py-10">
        <div className="mx-auto max-w-3xl">
          <ConnectorDashboard />
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[#E2DED7] bg-white">
        <div className="mx-auto max-w-6xl px-6 py-8 text-center text-sm text-[#6B6B72]">
          QBR Narrator Agent — built on the Mythos Governance Standard. The
          machine calculates and drafts; the CSM retains judgment and commitment.
        </div>
      </footer>
    </main>
  );
}
