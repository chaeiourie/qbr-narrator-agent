import { ShieldCheck } from "lucide-react";
import {
  PRESET_DEFINITIONS,
  type SecurityPresets,
} from "../../lib/security/presets";

/**
 * Security Presets Panel — no-code security & privacy controls.
 *
 * Renders the Tier-1 / Tier-2 governance toggles as friendly selects. The user
 * never edits a config file or runs a command.
 */
export function SecurityPresetsPanel({
  presets,
  onChange,
}: {
  presets: SecurityPresets;
  onChange: (next: SecurityPresets) => void;
}) {
  return (
    <div className="rounded-2xl border border-[#E2DED7] bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center gap-2">
        <ShieldCheck className="h-5 w-5 text-[#734E71]" />
        <h2 className="text-lg font-semibold text-[#221521]">
          Security &amp; Privacy
        </h2>
      </div>
      <div className="space-y-4">
        {PRESET_DEFINITIONS.map((preset) => (
          <div key={preset.key}>
            <label className="mb-1 block text-sm font-medium text-[#221521]">
              {preset.label}
            </label>
            <select
              value={presets[preset.key]}
              onChange={(e) =>
                onChange({ ...presets, [preset.key]: e.target.value } as SecurityPresets)
              }
              className="w-full rounded-lg border border-[#E2DED7] bg-white px-3 py-2 text-sm text-[#221521]"
            >
              {preset.options.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-[#6B6B72]">{preset.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
