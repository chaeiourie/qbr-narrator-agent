/**
 * QBR Narrator Agent — Mythos Security presets
 *
 * Centralizes the user-facing security toggles and maps them to the concrete
 * Tier-1 / Tier-2 controls they enable. The UI renders these as friendly
 * toggles; this module is the single source of truth for what each preset does.
 */

export type PiiMasking = "strict" | "balanced" | "off";
export type ExecutionScope = "read-only" | "read-write";
export type HumanApproval = "required" | "optional";
export type RedTeam = "always-on" | "off";

export interface SecurityPresets {
  piiMasking: PiiMasking;
  executionScope: ExecutionScope;
  humanApproval: HumanApproval;
  redTeamCheck: RedTeam;
}

export const DEFAULT_PRESETS: SecurityPresets = {
  piiMasking: "balanced",
  executionScope: "read-only",
  humanApproval: "required",
  redTeamCheck: "always-on",
};

export interface PresetDescription {
  key: keyof SecurityPresets;
  label: string;
  description: string;
  options: { value: string; label: string }[];
}

export const PRESET_DEFINITIONS: PresetDescription[] = [
  {
    key: "piiMasking",
    label: "PII & Secret Masking",
    description:
      "Strips customer emails, phone numbers, IDs, and API tokens before any outbound AI call. Controls LLM02/LLM05. Strict masks everything; Balanced keeps domain hints for context.",
    options: [
      { value: "strict", label: "Strict" },
      { value: "balanced", label: "Balanced" },
      { value: "off", label: "Off" },
    ],
  },
  {
    key: "executionScope",
    label: "Max Execution Scope",
    description:
      "Read-only means the agent can pull data but can never write back to Gainsight, Salesforce, or Zendesk. Read-write still requires a human gate for every write. Controls ASI04.",
    options: [
      { value: "read-only", label: "Read-Only" },
      { value: "read-write", label: "Read-Write" },
    ],
  },
  {
    key: "humanApproval",
    label: "Human Approval",
    description:
      "When Required, every write, dispatch, or commitment pauses for explicit sign-off. Controls the Irreversible Commitment Gate.",
    options: [
      { value: "required", label: "Required" },
      { value: "optional", label: "Optional" },
    ],
  },
  {
    key: "redTeamCheck",
    label: "Red-Team Check",
    description:
      "Always-on forces the agent to test disconfirming evidence and alternative hypotheses before presenting a risk narrative. Controls the anti-confirmation-bias check.",
    options: [
      { value: "always-on", label: "Always-On" },
      { value: "off", label: "Off" },
    ],
  },
];
