import { useMemo, useState } from "react";
import {
  CheckCircle2,
  FileText,
  Languages,
  Lock,
  Mic,
  Play,
  Sparkles,
  TriangleAlert,
} from "lucide-react";
import {
  analyseGaps,
  buildChecklist,
  buildSlides,
  resolveLanguage,
  secondLayerSuggestions,
  SUPPORTED_LANGUAGES,
  type Slide,
} from "../../lib/narratorEngine";
import { DEFAULT_PRESETS, type SecurityPresets } from "../../lib/security/presets";
import { SecurityPresetsPanel } from "./SecurityPresetsPanel";

/**
 * Narrator Workspace — the 6-stage flow.
 *
 * Stage 1 input & language parity · Stage 2 tone governance · Stage 3
 * second-layer thinking · Stage 4 dual generation (deck + checklist) ·
 * Stage 5 manager preview & approval. The machine drafts; the human approves.
 */
export function NarratorWorkspace() {
  const [customerName, setCustomerName] = useState("");
  const [language, setLanguage] = useState("en");
  const [recipientEmail, setRecipientEmail] = useState("");
  const [notes, setNotes] = useState("");
  const [tone, setTone] = useState("Formal");
  const [toneSample, setToneSample] = useState("");
  const [presets, setPresets] = useState<SecurityPresets>(DEFAULT_PRESETS);
  const [generated, setGenerated] = useState(false);
  const [activeTab, setActiveTab] = useState<"deck" | "checklist">("deck");
  const [approved, setApproved] = useState(false);

  const gaps = useMemo(() => (notes.trim() ? analyseGaps(notes) : []), [notes]);
  const suggestions = useMemo(() => secondLayerSuggestions(gaps), [gaps]);

  const slides: Slide[] = useMemo(() => {
    if (!generated) return [];
    return buildSlides({ customerName: customerName || "Unnamed Account", notes, tone });
  }, [generated, customerName, notes, tone]);

  const checklist = useMemo(
    () => (generated ? buildChecklist({ customerName: customerName || "Unnamed Account", language }) : ""),
    [generated, customerName, language],
  );

  const emailValid = !recipientEmail || /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(recipientEmail);

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      {/* Input panel */}
      <div className="space-y-6 lg:col-span-1">
        <div className="rounded-2xl border border-[#E2DED7] bg-white p-6 shadow-sm">
          <div className="mb-4 flex items-center gap-2">
            <FileText className="h-5 w-5 text-[#734E71]" />
            <h2 className="text-lg font-semibold text-[#221521]">
              Stage 1 — QBR Inputs
            </h2>
          </div>
          <div className="space-y-4">
            <Field label="Customer name">
              <input
                value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
                placeholder="e.g. Acme Corp"
                className="w-full rounded-lg border border-[#E2DED7] px-3 py-2 text-sm"
              />
            </Field>
            <Field label="Target language (deck + audio must match)">
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full rounded-lg border border-[#E2DED7] bg-white px-3 py-2 text-sm"
              >
                {Object.entries(SUPPORTED_LANGUAGES).map(([code, label]) => (
                  <option key={code} value={code}>
                    {label}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Recipient email">
              <input
                value={recipientEmail}
                onChange={(e) => setRecipientEmail(e.target.value)}
                placeholder="customer@company.com"
                className="w-full rounded-lg border border-[#E2DED7] px-3 py-2 text-sm"
              />
              {!emailValid && (
                <p className="mt-1 text-xs text-[#DC5F6C]">
                  That email address looks incomplete.
                </p>
              )}
            </Field>
            <Field label="Raw progress notes / metrics">
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Paste your rough notes — wins, ROI, risks, next steps…"
                rows={5}
                className="w-full rounded-lg border border-[#E2DED7] px-3 py-2 text-sm"
              />
            </Field>
          </div>

          {/* Stage 2 — tone governance */}
          <div className="mt-5 rounded-lg bg-[#F3EAF3] p-4">
            <div className="flex items-center gap-2">
              <Languages className="h-4 w-4 text-[#734E71]" />
              <p className="text-sm font-medium text-[#734E71]">
                Stage 2 — Tone: {tone} (Enterprise Executive)
              </p>
            </div>
            <p className="mt-1 text-xs text-[#734E71]">
              Default is Formal. Switch it, or attach a sample sentence for tone
              matching (audio samples trigger voice cloning).
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              {["Formal", "Warm", "Direct"].map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setTone(t)}
                  className={`rounded-full px-3 py-1 text-xs font-medium ${
                    tone === t
                      ? "bg-[#734E71] text-white"
                      : "border border-[#C38AC0] bg-white text-[#734E71]"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
            <input
              value={toneSample}
              onChange={(e) => setToneSample(e.target.value)}
              placeholder="Optional: paste a sample sentence for tone matching"
              className="mt-3 w-full rounded-lg border border-[#E2DED7] px-3 py-2 text-sm"
            />
          </div>

          <button
            type="button"
            onClick={() => setGenerated(true)}
            className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-[#734E71] px-4 py-2.5 text-sm font-medium text-white hover:bg-[#5e3f5c]"
          >
            <Sparkles className="h-4 w-4" />
            Generate deck + checklist
          </button>
        </div>

        {/* Stage 3 — second-layer thinking */}
        {suggestions.length > 0 && (
          <div className="rounded-2xl border border-[#E2DED7] bg-white p-6 shadow-sm">
            <div className="mb-3 flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-[#734E71]" />
              <h2 className="text-base font-semibold text-[#221521]">
                Stage 3 — Strengthen your QBR
              </h2>
            </div>
            <p className="mb-3 text-xs text-[#6B6B72]">
              These sections look thin in your notes. Add a line for each, or
              continue with professional defaults.
            </p>
            <ul className="space-y-2">
              {suggestions.map((s) => (
                <li key={s} className="text-sm text-[#46464d]">
                  • {s}
                </li>
              ))}
            </ul>
          </div>
        )}

        <SecurityPresetsPanel presets={presets} onChange={setPresets} />
      </div>

      {/* Output panel */}
      <div className="lg:col-span-2">
        {!generated ? (
          <div className="flex h-full min-h-[360px] flex-col items-center justify-center rounded-2xl border border-dashed border-[#D8D4CC] bg-white p-8 text-center">
            <Lock className="mb-3 h-8 w-8 text-[#D8D4CC]" />
            <p className="text-sm text-[#6B6B72]">
              Enter your QBR inputs, then press{" "}
              <span className="font-medium text-[#221521]">
                Generate deck + checklist
              </span>
              . Your bundle is produced behind the Mythos Security Shield.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Tabs */}
            <div className="flex gap-1 border-b border-[#E2DED7]">
              {(["deck", "checklist"] as const).map((tab) => (
                <button
                  key={tab}
                  type="button"
                  onClick={() => setActiveTab(tab)}
                  className={`-mb-px border-b-2 px-4 py-2 text-sm font-medium ${
                    activeTab === tab
                      ? "border-[#66A2A8] text-[#3F6E73]"
                      : "border-transparent text-[#6B6B72]"
                  }`}
                >
                  {tab === "deck" ? "Deliverable A — Deck" : "Deliverable B — Checklist"}
                </button>
              ))}
            </div>

            {activeTab === "deck" ? (
              <div className="space-y-4">
                {slides.map((s) => (
                  <div
                    key={s.index}
                    className="relative rounded-2xl border border-[#E2DED7] bg-white p-6 shadow-sm"
                  >
                    <button
                      type="button"
                      className="absolute right-4 top-4 inline-flex items-center gap-1.5 rounded-full bg-[#734E71] px-3 py-1.5 text-xs font-medium text-white hover:bg-[#5e3f5c]"
                      title="Play this slide's narration"
                    >
                      <Play className="h-3 w-3" />
                      Listen
                    </button>
                    <span className="inline-block rounded-full bg-[#F3EAF3] px-2.5 py-0.5 text-[11px] font-medium text-[#734E71]">
                      Slide {s.index} · {resolveLanguage(language)}
                    </span>
                    <h3 className="mt-3 text-lg font-semibold text-[#221521]">
                      {s.title}
                    </h3>
                    <ul className="mt-2 space-y-1">
                      {s.bullets.map((b, i) => (
                        <li key={i} className="text-sm text-[#46464d]">
                          • {b}
                        </li>
                      ))}
                    </ul>
                    <div className="mt-4 flex items-start gap-2 rounded-lg bg-[#F7F6F4] p-3 text-xs text-[#6B6B72]">
                      <Mic className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                      <p>
                        <span className="font-medium text-[#46464d]">
                          Narration ({resolveLanguage(language)}):
                        </span>{" "}
                        {s.narration}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="rounded-2xl border border-[#E2DED7] bg-white p-6 shadow-sm">
                <h3 className="mb-3 text-lg font-semibold text-[#221521]">
                  Setup &amp; Subscription Checklist
                </h3>
                <pre className="whitespace-pre-wrap text-xs leading-relaxed text-[#46464d]">
                  {checklist}
                </pre>
              </div>
            )}

            {/* Stage 5 — approval gate */}
            <div className="rounded-2xl border border-[#E2DED7] bg-white p-6 shadow-sm">
              <h3 className="text-base font-semibold text-[#221521]">
                Stage 5 — Manager approval
              </h3>
              <p className="mt-1 text-sm text-[#46464d]">
                Nothing is sent to the customer until you approve. Review both
                deliverables above, then approve to dispatch.
              </p>
              {approved ? (
                <div className="mt-3 flex items-center gap-2 rounded-lg bg-[#EAF4F4] p-3 text-sm text-[#3F6E73]">
                  <CheckCircle2 className="h-4 w-4" />
                  Approved — the bundle is queued for dispatch via your email
                  adapter.
                </div>
              ) : (
                <button
                  type="button"
                  onClick={() => setApproved(true)}
                  className="mt-3 inline-flex items-center gap-2 rounded-lg bg-[#66A2A8] px-4 py-2 text-sm font-medium text-white hover:bg-[#4f8489]"
                >
                  <CheckCircle2 className="h-4 w-4" />
                  Approve &amp; queue dispatch
                </button>
              )}
            </div>

            <div className="flex items-start gap-2 rounded-lg bg-[#F3EAF3] p-3 text-xs text-[#734E71]">
              <TriangleAlert className="mt-0.5 h-3.5 w-3.5 shrink-0" />
              <p>
                In this browser preview the deck, checklist, and dispatch are
                simulated. The Python engine (<span className="font-mono">engine/</span>)
                produces the real HTML deck, MP3 narration, and PDF/Markdown
                checklist — see the README for how to run it.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-[#221421]">{label}</label>
      {children}
    </div>
  );
}
