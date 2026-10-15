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
    claude_model: str
    claude_effort: str | None


def get_settings() -> Settings:
    model = os.getenv("CLAUDE_MODEL", "").strip()
    if not model:
        raise ConfigError("CLAUDE_MODEL is not set. Add it to .env (see .env.example).")
    effort = os.getenv("CLAUDE_EFFORT", "").strip() or None
    return Settings(claude_model=model, claude_effort=effort)
