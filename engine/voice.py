"""ElevenLabs voice layer — per-slide narration + Instant Voice Cloning.

This is the module behind the "Listen" button pinned to every slide. It does
two things:

  1. `synthesise_slide_audio` — turns each slide's narration text into a 20-30
     second MP3, in the SAME language as the deck (the MANDATORY LANGUAGE
     PARITY rule). One MP3 per slide.
  2. `clone_voice` — Stage 2 optional Instant Voice Cloning: if the CSM attaches
     an audio sample, it is uploaded to the ElevenLabs Instant Voice Cloning
     endpoint (`/v1/voices/add`) and the returned voice_id is used for every
     slide.

Reliability safeguard: if ELEVENLABS_API_KEY is absent, or the API times out,
the agent does NOT crash — it falls back to text-only slides (audio_path stays
None) and records the reason in the run log. The deck still renders.

Governance (Tier 1): the narration text is PII-redacted before it is sent to
ElevenLabs, and no audio bytes are ever sent anywhere except the ElevenLabs
synthesis endpoint. Voice cloning requires the speaker's consent — see the
README's "What This Does Not Cover".
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ELEVENLABS_API_BASE = "https://api.elevenlabs.io/v1"

# A calm, authoritative default voice id (ElevenLabs "Rachel"-class narrator).
# Overridden by ELEVENLABS_VOICE_ID or by an Instant Voice Cloning result.
DEFAULT_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
DEFAULT_MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")

# ElevenLabs accepts ISO 639-1 language codes directly for the multilingual model.
SUPPORTED_TTS_LANGUAGES = {"en", "zh", "es", "ja", "de", "fr", "pt", "ko"}


@dataclass
class VoiceResult:
    ok: bool
    audio_path: str | None = None
    voice_id: str | None = None
    reason: str = ""


def _api_key() -> str:
    return os.getenv("ELEVENLABS_API_KEY", "").strip()


def is_configured() -> bool:
    """True when a real ElevenLabs key is present (live voice is possible)."""
    return bool(_api_key())


def clone_voice(sample_path: str, name: str = "qbr-cloned-voice") -> VoiceResult:
    """Instant Voice Cloning — Stage 2, when the CSM attaches an audio sample.

    Uploads the sample to `/v1/voices/add` and returns the new voice_id. Requires
    the ElevenLabs Starter plan or higher. If no key is configured, returns a
    non-fatal failure so the caller can fall back to the default narrator voice.
    """
    key = _api_key()
    if not key:
        return VoiceResult(ok=False, reason="ELEVENLABS_API_KEY not set — skipping voice cloning.")
    path = Path(sample_path)
    if not path.exists():
        return VoiceResult(ok=False, reason=f"Voice sample not found: {sample_path}")

    boundary = "----qbrnarratorboundary"
    file_bytes = path.read_bytes()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="name"\r\n\r\n{name}\r\n'
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="files"; filename="{path.name}"\r\n'
        f"Content-Type: audio/mpeg\r\n\r\n"
    ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        f"{ELEVENLABS_API_BASE}/voices/add",
        data=body,
        headers={
            "xi-api-key": key,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            return VoiceResult(ok=True, voice_id=payload.get("voice_id"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return VoiceResult(ok=False, reason=f"Voice cloning failed: {exc}")


def synthesise_slide_audio(
    text: str,
    language: str,
    out_path: str,
    voice_id: str | None = None,
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    style: float = 0.0,
) -> VoiceResult:
    """Synthesise one slide's narration to an MP3 file.

    `language` is the deck's target language; the narration text is already in
    that language (language parity is enforced upstream), and the multilingual
    model speaks it natively. Voice settings (stability / similarity_boost /
    style) are tuned by Stage 2 tone analysis.
    """
    key = _api_key()
    if not key:
        return VoiceResult(ok=False, reason="ELEVENLABS_API_KEY not set — text-only deck.")

    payload = json.dumps(
        {
            "text": text,
            "model_id": DEFAULT_MODEL_ID,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "use_speaker_boost": True,
            },
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        f"{ELEVENLABS_API_BASE}/text-to-speech/{voice_id or DEFAULT_VOICE_ID}",
        data=payload,
        headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"},
        method="POST",
    )
    dest = Path(out_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            dest.write_bytes(resp.read())
            return VoiceResult(ok=True, audio_path=str(dest), voice_id=voice_id or DEFAULT_VOICE_ID)
    except (urllib.error.URLError, TimeoutError) as exc:
        # Reliability safeguard: never crash the run on a voice timeout.
        return VoiceResult(ok=False, reason=f"Voice synthesis timed out or failed: {exc}")


def tone_to_voice_settings(tone: str) -> dict:
    """Map the Stage 2 tone setting to ElevenLabs voice settings.

    Formal (default) = steady, authoritative. Warm = more expressive. Direct =
    flatter, faster-feeling delivery.
    """
    table = {
        "Formal": {"stability": 0.65, "similarity_boost": 0.80, "style": 0.0},
        "Warm": {"stability": 0.40, "similarity_boost": 0.75, "style": 0.35},
        "Direct": {"stability": 0.80, "similarity_boost": 0.70, "style": 0.0},
    }
    return table.get(tone, table["Formal"])
