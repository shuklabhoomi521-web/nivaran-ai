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
    gemini_backup_model: str        # asked too when the main text model is slow ("hedging"); "none" turns it off
    gemini_hedge_seconds: float
    claude_effort: str | None
    groq_model: str
    groq_rpm: int
    groq_timeout: float
    stt_provider: str        # "gemini" (default) or "fake" in tests
    tts_provider: str
    gemini_stt_model: str
    gemini_tts_model: str
    gemini_tts_voice: str
    gemini_prompt_stt_model: str   # general Gemini model used for transcription-by-prompt (STT_PROVIDER=gemini_prompt)
    sarvam_stt_model: str
    sarvam_tts_model: str
    sarvam_rpm: int
    sarvam_credit_rupees: float       # free credit Sarvam gave us
    sarvam_credit_already_spent: float  # estimate of what tests used before the ledger existed (only used when the ledger file is new)
    stt_fallback: str                  # backup speech-to-text provider ("none" to disable)
    tts_fallback: str
    sarvam_company_keyterms: bool   # give Sarvam v4 the directory's company names so it spells them right
    sarvam_hinglish_mode: str   # translit | transcribe | codemix : how Sarvam writes Hindi-English speech
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
    if provider not in ("gemini", "anthropic", "groq"):
        raise ConfigError("LLM_PROVIDER must be 'gemini', 'groq' or 'anthropic'.")
    return Settings(
        provider=provider,
        gemini_model=os.getenv("GEMINI_MODEL", "").strip() or "gemini-3.5-flash-lite",
        gemini_rpm=_int("GEMINI_RPM", 5),
        gemini_rpd=_int("GEMINI_RPD", 0),
        gemini_backup_model=os.getenv("GEMINI_BACKUP_MODEL", "").strip() or "gemini-3.6-flash",
        gemini_hedge_seconds=float(os.getenv("GEMINI_HEDGE_SECONDS", "").strip() or 4),
        claude_model=os.getenv("CLAUDE_MODEL", "").strip(),
        claude_effort=os.getenv("CLAUDE_EFFORT", "").strip() or None,
        groq_model=os.getenv("GROQ_MODEL", "").strip() or "openai/gpt-oss-120b",
        groq_rpm=_int("GROQ_RPM", 25),
        groq_timeout=float(os.getenv("GROQ_TIMEOUT", "").strip() or 8),
        stt_provider=(os.getenv("STT_PROVIDER", "").strip() or "sarvam").lower(),
        tts_provider=(os.getenv("TTS_PROVIDER", "").strip() or "sarvam").lower(),
        gemini_stt_model=os.getenv("GEMINI_STT_MODEL", "").strip() or "gemini-3.5-transcribe",
        gemini_tts_model=os.getenv("GEMINI_TTS_MODEL", "").strip() or "gemini-3.8-flash-lite-tts",
        gemini_tts_voice=os.getenv("GEMINI_TTS_VOICE", "").strip() or "Kore",
        gemini_prompt_stt_model=os.getenv("GEMINI_PROMPT_STT_MODEL", "").strip() or "gemini-3.5-flash-lite",
        sarvam_stt_model=os.getenv("SARVAM_STT_MODEL", "").strip() or "saaras:v4",
        sarvam_tts_model=os.getenv("SARVAM_TTS_MODEL", "").strip() or "bulbul:v4-flash",
        sarvam_rpm=_int("SARVAM_RPM", 10),
        sarvam_credit_rupees=float(os.getenv("SARVAM_CREDIT_RUPEES", "").strip() or 100),
        sarvam_credit_already_spent=float(os.getenv("SARVAM_CREDIT_ALREADY_SPENT", "").strip() or 29.7),
        stt_fallback=(os.getenv("STT_FALLBACK", "").strip() or "gemini_prompt").lower(),
        tts_fallback=(os.getenv("TTS_FALLBACK", "").strip() or "gemini").lower(),
        sarvam_company_keyterms=(os.getenv("SARVAM_COMPANY_KEYTERMS", "").strip().lower() or "true") != "false",
        sarvam_hinglish_mode=os.getenv("SARVAM_HINGLISH_MODE", "").strip() or "codemix",
        speech_rpm=_int("SPEECH_RPM", 6),
        speech_rpd=_int("SPEECH_RPD", 0),
    )
