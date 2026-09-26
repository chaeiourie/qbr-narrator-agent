/**
 * QBR Narrator Agent — CS Tool Integration Registry (TS mirror)
 *
 * Mirrors engine/integrations.py. Scoped against the pipeline's "CS Tool
 * Registry" skill. No integration is faked: tools with no usable API path for
 * this lightweight build are marked status "watch" and are NOT wired into the
 * connector dashboard as if they worked.
 */

export type IntegrationStatus = "integrated" | "watch";

export interface Integration {
  id: string;
  name: string;
  category: string;
  whatItDoes: string;
  authType: string;
  configKeys: string[];
  status: IntegrationStatus;
  readOnlyByDefault: boolean;
  note?: string;
}

export const INTEGRATIONS: Integration[] = [
  {
    id: "anthropic",
    name: "Anthropic Claude",
    category: "LLM — deck text, translation & tone analysis",
    whatItDoes: "Writes and translates the slide text and analyses tone samples.",
    authType: "API key",
    configKeys: ["ANTHROPIC_API_KEY"],
    status: "integrated",
    readOnlyByDefault: true,
    note: "Needs Build Tier 1 prepaid API credit ($5 min) — an API key, not a Claude Pro subscription.",
  },
  {
    id: "elevenlabs",
    name: "ElevenLabs",
    category: "Voice synthesis & Instant Voice Cloning",
    whatItDoes: "Generates the per-slide spoken narration in the deck's language.",
    authType: "API key",
    configKeys: ["ELEVENLABS_API_KEY"],
    status: "integrated",
    readOnlyByDefault: true,
    note: "Requires the Starter plan ($5/mo) or higher to unlock Instant Voice Cloning and commercial voice generation.",
  },
  {
    id: "gainsight",
    name: "Gainsight",
    category: "Health scoring / CS platform",
    whatItDoes: "Pull health scores, usage, and account attributes for the QBR.",
    authType: "API key",
    configKeys: ["GAINSIGHT_API_KEY"],
    status: "integrated",
    readOnlyByDefault: true,
  },
  {
    id: "salesforce",
    name: "Salesforce",
    category: "CRM",
    whatItDoes: "Pull MRR, account objects, and opportunity/renewal data.",
    authType: "OAuth2 / JWT",
    configKeys: [
      "SALESFORCE_INSTANCE_URL",
      "SALESFORCE_CLIENT_ID",
      "SALESFORCE_CLIENT_SECRET",
    ],
    status: "integrated",
    readOnlyByDefault: true,
  },
  {
    id: "zendesk",
    name: "Zendesk",
    category: "Support / ticket data",
    whatItDoes: "Pull support ticket volume, sentiment, and open items.",
    authType: "API token",
    configKeys: ["ZENDESK_SUBDOMAIN", "ZENDESK_API_TOKEN"],
    status: "integrated",
    readOnlyByDefault: true,
  },
  {
    id: "hubspot",
    name: "HubSpot",
    category: "CRM / comms",
    whatItDoes: "Pull company records, tickets, and engagement signals.",
    authType: "API key / OAuth2",
    configKeys: ["HUBSPOT_API_KEY"],
    status: "integrated",
    readOnlyByDefault: true,
  },
  {
    id: "totango",
    name: "Totango",
    category: "Health scoring / CS platform",
    whatItDoes: "Pull customer health and journey data.",
    authType: "API key",
    configKeys: ["TOTANGO_API_KEY"],
    status: "integrated",
    readOnlyByDefault: true,
  },
  {
    id: "churnzero",
    name: "ChurnZero",
    category: "Health scoring / churn",
    whatItDoes: "Pull health scores, usage signals, and playbook data.",
    authType: "API key",
    configKeys: ["CHURNZERO_API_KEY"],
    status: "integrated",
    readOnlyByDefault: true,
  },
  {
    id: "gong",
    name: "Gong",
    category: "Call analytics / revenue intelligence",
    whatItDoes: "Pull call sentiment and meeting signals.",
    authType: "OAuth2",
    configKeys: ["GONG_CLIENT_ID", "GONG_CLIENT_SECRET"],
    status: "watch",
    readOnlyByDefault: true,
    note: "Requires a Gong OAuth2 app (client credentials) that is not available as a stable no-code path in this lightweight build. Marked 'watch' in the CS Tool Registry; not wired as a working connector.",
  },
];

export function integratedIntegrations(): Integration[] {
  return INTEGRATIONS.filter((i) => i.status === "integrated");
}

export function watchIntegrations(): Integration[] {
  return INTEGRATIONS.filter((i) => i.status === "watch");
}
