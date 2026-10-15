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
    )
