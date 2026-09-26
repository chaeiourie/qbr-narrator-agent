"""Pluggable email adapters.

An abstract BaseEmailAdapter with plug-and-play implementations:
  - LocalMockAdapter:      saves the deck, MP3s, and checklist to /output (free testing)
  - SendGridAdapter:       sends the customer email with the presentation link
  - MailchimpAdapter:      sends via the Mailchimp Transactional API
  - SmtpAdapter:           sends via standard SMTP (Gmail / Outlook)

Adapters are read-only with respect to customer systems: the ONLY outbound
action any adapter performs is sending the approved email. Nothing is written
back to a downstream CS tool.
"""

from __future__ import annotations

import json
import os
import smtplib
import ssl
from abc import ABC, abstractmethod
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path


@dataclass
class EmailPayload:
    to: str
    subject: str
    body: str
    deck_path: str | None = None
    checklist_path: str | None = None


class BaseEmailAdapter(ABC):
    """Abstract base. Every adapter must implement `send`."""

    name: str = "base"

    @abstractmethod
    def send(self, payload: EmailPayload) -> dict:
        """Dispatch the email. Returns a result dict with at least {sent: bool}."""
        raise NotImplementedError


class LocalMockAdapter(BaseEmailAdapter):
    """Free local adapter. Writes everything to OUTPUT_DIR, sends nothing.

    This is the default (EMAIL_ADAPTER=local) and the safe way to test the full
    pipeline without spending money or emailing a real customer.
    """

    name = "local"

    def __init__(self, output_dir: str | None = None) -> None:
        self.output_dir = Path(output_dir or os.getenv("OUTPUT_DIR", "./output"))

    def send(self, payload: EmailPayload) -> dict:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        record = {
            "to": payload.to,
            "subject": payload.subject,
            "body": payload.body,
            "deck_path": payload.deck_path,
            "checklist_path": payload.checklist_path,
            "mode": "local-mock",
        }
        out_file = self.output_dir / "last_dispatch.json"
        out_file.write_text(json.dumps(record, indent=2), encoding="utf-8")
        return {"sent": False, "mode": "local-mock", "written_to": str(out_file)}


class SendGridAdapter(BaseEmailAdapter):
    """Sends via the SendGrid v3 API (free tier: 100 emails/day)."""

    name = "sendgrid"

    def __init__(self, api_key: str | None = None, from_email: str | None = None) -> None:
        self.api_key = api_key or os.getenv("SENDGRID_API_KEY", "")
        self.from_email = from_email or os.getenv("SENDGRID_FROM_EMAIL", "")

    def send(self, payload: EmailPayload) -> dict:
        if not self.api_key or not self.from_email:
            raise RuntimeError("SendGrid requires SENDGRID_API_KEY and SENDGRID_FROM_EMAIL.")
        import urllib.request

        data = json.dumps(
            {
                "personalizations": [{"to": [{"email": payload.to}]}],
                "from": {"email": self.from_email},
                "subject": payload.subject,
                "content": [{"type": "text/plain", "value": payload.body}],
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            "https://api.sendgrid.com/v3/mail/send",
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return {"sent": resp.status in (200, 202), "mode": "sendgrid", "status": resp.status}


class MailchimpAdapter(BaseEmailAdapter):
    """Sends via the Mailchimp Transactional (Mandrill) API."""

    name = "mailchimp"

    def __init__(self, api_key: str | None = None, from_email: str | None = None) -> None:
        self.api_key = api_key or os.getenv("MAILCHIMP_API_KEY", "")
        self.from_email = from_email or os.getenv("MAILCHIMP_FROM_EMAIL", "")

    def send(self, payload: EmailPayload) -> dict:
        if not self.api_key or not self.from_email:
            raise RuntimeError("Mailchimp requires MAILCHIMP_API_KEY and MAILCHIMP_FROM_EMAIL.")
        import urllib.request

        data = json.dumps(
            {
                "key": self.api_key,
                "message": {
                    "from_email": self.from_email,
                    "to": [{"email": payload.to, "type": "to"}],
                    "subject": payload.subject,
                    "text": payload.body,
                },
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            "https://mandrillapp.com/api/1.0/messages/send.json",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return {"sent": resp.status == 200, "mode": "mailchimp", "status": resp.status}


class SmtpAdapter(BaseEmailAdapter):
    """Sends via standard SMTP (Gmail app password, Outlook, any provider)."""

    name = "smtp"

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
        from_email: str | None = None,
    ) -> None:
        self.host = host or os.getenv("SMTP_HOST", "")
        self.port = int(port or os.getenv("SMTP_PORT", "587"))
        self.user = user or os.getenv("SMTP_USER", "")
        self.password = password or os.getenv("SMTP_PASSWORD", "")
        self.from_email = from_email or os.getenv("SMTP_FROM_EMAIL", self.user)

    def send(self, payload: EmailPayload) -> dict:
        if not self.host or not self.user or not self.password:
            raise RuntimeError("SMTP requires SMTP_HOST, SMTP_USER and SMTP_PASSWORD.")
        msg = EmailMessage()
        msg["From"] = self.from_email
        msg["To"] = payload.to
        msg["Subject"] = payload.subject
        msg.set_content(payload.body)
        context = ssl.create_default_context()
        with smtplib.SMTP(self.host, self.port, timeout=30) as server:
            server.starttls(context=context)
            server.login(self.user, self.password)
            server.send_message(msg)
        return {"sent": True, "mode": "smtp"}


_ADAPTERS: dict[str, type[BaseEmailAdapter]] = {
    "local": LocalMockAdapter,
    "sendgrid": SendGridAdapter,
    "mailchimp": MailchimpAdapter,
    "smtp": SmtpAdapter,
}


def get_adapter(name: str | None = None) -> BaseEmailAdapter:
    """Return the configured adapter. Defaults to the free local mock."""
    key = (name or os.getenv("EMAIL_ADAPTER", "local")).lower()
    adapter_cls = _ADAPTERS.get(key)
    if adapter_cls is None:
        raise ValueError(
            f"Unknown EMAIL_ADAPTER '{key}'. Choose one of: {', '.join(_ADAPTERS)}."
        )
    return adapter_cls()
