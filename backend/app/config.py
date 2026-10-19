"""Settings come from environment variables (loaded from .env). No keys in code."""
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class Settings:
    provider: str            # "gemini" (default, free) or "anthropic"
    gemini_model: str
    gemini_rpm: int          # max requests per minute we allow ourselves
    gemini_rpd: int          # max requests per day we allow ourselves (0 = no local cap)
    claude_model: str
    claude_effort: str | None
    stt_provider: str        # "gemini" (default) or "fake" in tests
    tts_provider: str
    gemini_stt_model: str
    gemini_tts_model: str
    gemini_tts_voice: str
    gemini_prompt_stt_model: str   # general Gemini model used for transcription-by-prompt (STT_PROVIDER=gemini_prompt)
    sarvam_stt_model: str
    sarvam_tts_model: str
    sarvam_rpm: int
    speech_rpm: int          # our own speed limit for audio calls
    speech_rpd: int


def _int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    try:
        return int(raw) if raw else default
    except ValueError:
        raise ConfigError(f"{name} must be a whole number, got {raw!r}")


def get_settings() -> Settings:
    provider = (os.getenv("LLM_PROVIDER", "").strip() or "gemini").lower()
    if provider not in ("gemini", "anthropic"):
        raise ConfigError("LLM_PROVIDER must be 'gemini' or 'anthropic'.")
    return Settings(
        provider=provider,
        gemini_model=os.getenv("GEMINI_MODEL", "").strip() or "gemini-3.5-flash-lite",
        gemini_rpm=_int("GEMINI_RPM", 5),
        gemini_rpd=_int("GEMINI_RPD", 0),
        claude_model=os.getenv("CLAUDE_MODEL", "").strip(),
        claude_effort=os.getenv("CLAUDE_EFFORT", "").strip() or None,
        stt_provider=(os.getenv("STT_PROVIDER", "").strip() or "gemini").lower(),
        tts_provider=(os.getenv("TTS_PROVIDER", "").strip() or "gemini").lower(),
        gemini_stt_model=os.getenv("GEMINI_STT_MODEL", "").strip() or "gemini-3.5-transcribe",
        gemini_tts_model=os.getenv("GEMINI_TTS_MODEL", "").strip() or "gemini-3.8-flash-tts",
        gemini_tts_voice=os.getenv("GEMINI_TTS_VOICE", "").strip() or "Kore",
        gemini_prompt_stt_model=os.getenv("GEMINI_PROMPT_STT_MODEL", "").strip() or "gemini-3.5-flash-lite",
        sarvam_stt_model=os.getenv("SARVAM_STT_MODEL", "").strip() or "saaras:v3",
        sarvam_tts_model=os.getenv("SARVAM_TTS_MODEL", "").strip() or "bulbul:v4-flash",
        sarvam_rpm=_int("SARVAM_RPM", 10),
        speech_rpm=_int("SPEECH_RPM", 6),
        speech_rpd=_int("SPEECH_RPD", 0),
    )
