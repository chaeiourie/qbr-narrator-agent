import { useState } from "react";
import { CheckCircle2, Eye, Plug, ShieldAlert } from "lucide-react";
import { INTEGRATIONS } from "../../lib/integrations/registry";

/**
 * Connector Dashboard — no-code CS tool connectors.
 *
 * Each row shows a name, a visual status (Connected / Disconnected), a no-code
 * action, and an ON/OFF toggle. Never raw JSON for the end user. Tools marked
 * "watch" are shown honestly as "Not available" rather than as if they worked.
 */
export function ConnectorDashboard() {
  const [enabled, setEnabled] = useState<Record<string, boolean>>({});

  return (
    <div className="rounded-2xl border border-[#E2DED7] bg-white p-6 shadow-sm">
      <div className="mb-5 flex items-center gap-2">
        <Plug className="h-5 w-5 text-[#734E71]" />
        <h2 className="text-lg font-semibold text-[#221521]">
          Connect your tools
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
  );
}
