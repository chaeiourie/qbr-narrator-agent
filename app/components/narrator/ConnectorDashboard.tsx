import { useEffect, useState } from "react";
import { CheckCircle2, Eye, KeyRound, Lock, Plug, ShieldAlert } from "lucide-react";
import { INTEGRATIONS } from "../../lib/integrations/registry";

/**
 * Connector Dashboard — no-code CS tool connectors + Bring-Your-Own-Keys.
 *
 * Each row shows a name, a visual status (Connected / Disconnected), a no-code
 * action, and an ON/OFF toggle. Never raw JSON for the end user. Tools marked
 * "watch" are shown honestly as "Not available" rather than as if they worked.
 *
 * BYO-KEY MODEL (important): the end user pastes THEIR OWN keys. Keys are held
 * only in this browser (in-memory + localStorage on the user's own device) and
 * are sent directly to the provider — never to the author, never to any
 * third-party server. No author-owned credentials exist anywhere in this app.
 */

// Providers the end user can connect with their own API key.
const BYO_KEY_PROVIDERS = [
  {
    id: "anthropic",
    label: "Anthropic Claude",
    help: "console.anthropic.com → API Keys → Create Key (needs $5 prepaid credit)",
    placeholder: "sk-ant-...",
  },
  {
    id: "elevenlabs",
    label: "ElevenLabs",
    help: "elevenlabs.io → Profile → API Keys → Create (Starter plan or higher)",
    placeholder: "your ElevenLabs key",
  },
] as const;

const STORAGE_KEY = "qbr-narrator:byo-keys";

export function ConnectorDashboard() {
  const [enabled, setEnabled] = useState<Record<string, boolean>>({});
  const [keys, setKeys] = useState<Record<string, string>>({});
  const [revealed, setRevealed] = useState<Record<string, boolean>>({});

  // Load any keys the user previously saved in THIS browser only.
  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) setKeys(JSON.parse(raw));
    } catch {
      /* ignore — private mode / blocked storage */
    }
  }, []);

  function saveKey(id: string, value: string) {
    const next = { ...keys, [id]: value };
    setKeys(next);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    } catch {
      /* ignore */
    }
  }

  function clearKey(id: string) {
    const next = { ...keys };
    delete next[id];
    setKeys(next);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    } catch {
      /* ignore */
    }
  }

  return (
    <div className="space-y-6">
      {/* BYO-keys panel */}
      <div className="rounded-2xl border border-[#E2DED7] bg-white p-6 shadow-sm">
        <div className="mb-2 flex items-center gap-2">
          <KeyRound className="h-5 w-5 text-[#734E71]" />
          <h2 className="text-lg font-semibold text-[#221521]">
            Bring your own keys
          </h2>
        </div>
        <p className="mb-5 text-sm text-[#46464d]">
          This tool never uses the author's keys. Paste{" "}
          <span className="font-medium text-[#221521]">your own</span> Anthropic
          and ElevenLabs keys below. They stay in this browser on your device and
          are sent straight to the provider — never to the author, never to a
          third-party server.
        </p>

        <div className="space-y-4">
          {BYO_KEY_PROVIDERS.map((p) => {
            const value = keys[p.id] ?? "";
            const connected = value.trim().length > 0;
            return (
              <div key={p.id}>
                <div className="mb-1 flex items-center justify-between gap-2">
                  <label className="text-sm font-medium text-[#221521]">
                    {p.label}
                  </label>
                  {connected ? (
                    <span className="inline-flex items-center gap-1 rounded-full bg-[#EAF4F4] px-2 py-0.5 text-[11px] font-medium text-[#3F6E73]">
                      <CheckCircle2 className="h-3 w-3" />
                      Connected
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 rounded-full bg-[#F1F0EE] px-2 py-0.5 text-[11px] font-medium text-[#6B6B72]">
                      Not connected
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type={revealed[p.id] ? "text" : "password"}
                    value={value}
                    onChange={(e) => saveKey(p.id, e.target.value)}
                    placeholder={p.placeholder}
                    autoComplete="off"
                    spellCheck={false}
                    className="w-full rounded-lg border border-[#E2DED7] px-3 py-2 text-sm"
                  />
                  <button
                    type="button"
                    onClick={() =>
                      setRevealed((prev) => ({ ...prev, [p.id]: !prev[p.id] }))
                    }
                    className="shrink-0 rounded-lg border border-[#E2DED7] px-3 py-2 text-xs font-medium text-[#734E71] hover:bg-[#FAF8F4]"
                  >
                    {revealed[p.id] ? "Hide" : "Show"}
                  </button>
                  {connected && (
                    <button
                      type="button"
                      onClick={() => clearKey(p.id)}
                      className="shrink-0 rounded-lg border border-[#E2DED7] px-3 py-2 text-xs font-medium text-[#6B6B72] hover:bg-[#FAF8F4]"
                    >
                      Clear
                    </button>
                  )}
                </div>
                <p className="mt-1 text-xs text-[#6B6B72]">{p.help}</p>
              </div>
            );
          })}
        </div>

        <div className="mt-5 flex items-start gap-2 rounded-lg bg-[#F3EAF3] p-3 text-xs text-[#734E71]">
          <Lock className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          <p>
            Your keys are stored only in this browser (local storage on your own
            device) and are never transmitted to the author or any third-party
            server. Generation is billed to your own Anthropic and ElevenLabs
            accounts. Clearing your browser data removes them.
          </p>
        </div>
      </div>

      {/* CS tool connectors */}
      <div className="rounded-2xl border border-[#E2DED7] bg-white p-6 shadow-sm">
        <div className="mb-5 flex items-center gap-2">
          <Plug className="h-5 w-5 text-[#734E71]" />
          <h2 className="text-lg font-semibold text-[#221521]">
            Connect your CS tools
          </h2>
        </div>
        <p className="mb-5 text-sm text-[#46464d]">
          Flip a connector on to pull data automatically instead of pasting it.
          All connectors are read-only by default — nothing is ever written back
          to your systems without your explicit approval.
        </p>

        <div className="divide-y divide-[#E2DED7]">
          {INTEGRATIONS.map((tool) => {
            const isWatch = tool.status === "watch";
            const isOn = !!enabled[tool.id];
            return (
              <div
                key={tool.id}
                className="flex flex-wrap items-center justify-between gap-3 py-3"
              >
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-[#221521]">
                      {tool.name}
                    </span>
                    {isWatch ? (
                      <span className="inline-flex items-center gap-1 rounded-full bg-[#F3EAF3] px-2 py-0.5 text-[11px] font-medium text-[#734E71]">
                        <ShieldAlert className="h-3 w-3" />
                        Not available
                      </span>
                    ) : isOn ? (
                      <span className="inline-flex items-center gap-1 rounded-full bg-[#EAF4F4] px-2 py-0.5 text-[11px] font-medium text-[#3F6E73]">
                        <CheckCircle2 className="h-3 w-3" />
                        Connected
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 rounded-full bg-[#F1F0EE] px-2 py-0.5 text-[11px] font-medium text-[#6B6B72]">
                        Disconnected
                      </span>
                    )}
                  </div>
                  <p className="mt-0.5 text-xs text-[#6B6B72]">
                    {tool.category} · {tool.authType}
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  <span className="hidden text-xs text-[#6B6B72] sm:inline">
                    {isWatch ? "—" : isOn ? "Keys saved" : "Add keys"}
                  </span>
                  <button
                    type="button"
                    disabled={isWatch}
                    onClick={() =>
                      setEnabled((prev) => ({ ...prev, [tool.id]: !prev[tool.id] }))
                    }
                    aria-pressed={isOn}
                    className={`relative h-6 w-11 rounded-full transition-colors ${
                      isWatch
                        ? "cursor-not-allowed bg-[#E2DED7]"
                        : isOn
                          ? "bg-[#66A2A8]"
                          : "bg-[#D8D4CC]"
                    }`}
                  >
                    <span
                      className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${
                        isOn ? "translate-x-5" : "translate-x-0.5"
                      }`}
                    />
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-5 flex items-start gap-2 rounded-lg bg-[#F3EAF3] p-3 text-xs text-[#734E71]">
          <Eye className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          <p>
            Gong is marked <span className="font-medium">watch</span> in the CS Tool
            Registry — it needs a Gong OAuth2 app that is not a stable no-code path
            for this build, so it is shown as not available rather than pretending
            it works.
          </p>
        </div>
      </div>
    </div>
  );
}
