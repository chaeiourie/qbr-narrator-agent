"""QBR Narrator Agent — CS Tool Integration Registry.

Scoped against the pipeline's "CS Tool Registry" skill. Each integration is a
named, swappable module with a REAL config surface (env keys, auth type, and how
it connects). No integration is faked: tools with no usable API path for this
lightweight build are marked status "watch" and are NOT wired into the connector
dashboard as if they worked.

Scope decision for QBR Narrator Agent:
  - Gainsight  (scoped)  -> integrated  (API key, GAINSIGHT_API_KEY)
  - Salesforce (scoped)  -> integrated  (OAuth2/JWT, SALESFORCE_* keys)
  - Zendesk    (scoped)  -> integrated  (API token, ZENDESK_* keys)
  - HubSpot    (scoped)  -> integrated  (API key, HUBSPOT_API_KEY)
  - Totango    (scoped)  -> integrated  (API key, TOTANGO_API_KEY)
  - ChurnZero  (scoped)  -> integrated  (API key, CHURNZERO_API_KEY)
  - Gong       (watch)   -> NOT wired   (OAuth2 app required; no stable public
                                          token path for a lightweight no-code
                                          tool. Marked watch in the registry.)
"""

from __future__ import annotations

from dataclasses import dataclass, field

# AI / generation services this agent depends on (not CS platforms, but real
# integrations with their own auth + config surface).
AI_SERVICES = [
    {
        "id": "anthropic",
        "name": "Anthropic Claude",
        "category": "LLM — deck text, translation & tone analysis",
        "auth_type": "API key",
        "config_keys": ["ANTHROPIC_API_KEY"],
        "status": "integrated",
        "note": "Requires Build Tier 1 prepaid API credit ($5 min) — an API key, not a Claude Pro subscription.",
    },
    {
        "id": "elevenlabs",
        "name": "ElevenLabs",
        "category": "Voice synthesis & Instant Voice Cloning",
        "auth_type": "API key",
        "config_keys": ["ELEVENLABS_API_KEY"],
        "status": "integrated",
        "note": "Requires Starter plan ($5/mo) or higher to unlock Instant Voice Cloning and commercial voice generation.",
    },
]


@dataclass
class Integration:
    id: str
    name: str
    category: str
    what_it_does: str
    auth_type: str
    config_keys: list[str] = field(default_factory=list)
    env_example: dict[str, str] = field(default_factory=dict)
    status: str = "integrated"  # "integrated" | "watch"
    read_only_by_default: bool = True
    note: str = ""


INTEGRATIONS: list[Integration] = [
    Integration(
        id="gainsight",
        name="Gainsight",
        category="Health scoring / CS platform",
        what_it_does="Pull health scores, usage, and account attributes for the QBR.",
        auth_type="API key",
        config_keys=["GAINSIGHT_API_KEY"],
        env_example={"GAINSIGHT_API_KEY": "gainsight_xxxxx"},
    ),
    Integration(
        id="salesforce",
        name="Salesforce",
        category="CRM",
        what_it_does="Pull MRR, account objects, and opportunity/renewal data.",
        auth_type="OAuth2 / JWT",
        config_keys=[
            "SALESFORCE_INSTANCE_URL",
            "SALESFORCE_CLIENT_ID",
            "SALESFORCE_CLIENT_SECRET",
        ],
        env_example={
            "SALESFORCE_INSTANCE_URL": "https://your-org.my.salesforce.com",
            "SALESFORCE_CLIENT_ID": "3MVG9...",
            "SALESFORCE_CLIENT_SECRET": "xxxxx",
        },
    ),
    Integration(
        id="zendesk",
        name="Zendesk",
        category="Support / ticket data",
        what_it_does="Pull support ticket volume, sentiment, and open items.",
        auth_type="API token",
        config_keys=["ZENDESK_SUBDOMAIN", "ZENDESK_API_TOKEN"],
        env_example={"ZENDESK_SUBDOMAIN": "yourcompany", "ZENDESK_API_TOKEN": "xxxxx"},
    ),
    Integration(
        id="hubspot",
        name="HubSpot",
        category="CRM / comms",
        what_it_does="Pull company records, tickets, and engagement signals.",
        auth_type="API key / OAuth2",
        config_keys=["HUBSPOT_API_KEY"],
        env_example={"HUBSPOT_API_KEY": "pat-xxxxx"},
    ),
    Integration(
        id="totango",
        name="Totango",
        category="Health scoring / CS platform",
        what_it_does="Pull customer health and journey data.",
        auth_type="API key",
        config_keys=["TOTANGO_API_KEY"],
        env_example={"TOTANGO_API_KEY": "totango_xxxxx"},
    ),
    Integration(
        id="churnzero",
        name="ChurnZero",
        category="Health scoring / churn",
        what_it_does="Pull health scores, usage signals, and playbook data.",
        auth_type="API key",
        config_keys=["CHURNZERO_API_KEY"],
        env_example={"CHURNZERO_API_KEY": "cz_xxxxx"},
    ),
    Integration(
        id="gong",
        name="Gong",
        category="Call analytics / revenue intelligence",
        what_it_does="Pull call sentiment and meeting signals.",
        auth_type="OAuth2",
        config_keys=["GONG_CLIENT_ID", "GONG_CLIENT_SECRET"],
        env_example={"GONG_CLIENT_ID": "gong_client_id", "GONG_CLIENT_SECRET": "xxxxx"},
        status="watch",
        note=(
            "Requires a Gong OAuth2 app (client credentials) that is not available as a "
            "stable no-code path in this lightweight build. Marked 'watch' in the CS Tool "
            "Registry; not wired into the connector dashboard as if it worked."
        ),
    ),
]


def get_integration(integration_id: str) -> Integration | None:
    return next((i for i in INTEGRATIONS if i.id == integration_id), None)


def integrated_integrations() -> list[Integration]:
    return [i for i in INTEGRATIONS if i.status == "integrated"]


def watch_integrations() -> list[Integration]:
    return [i for i in INTEGRATIONS if i.status == "watch"]
