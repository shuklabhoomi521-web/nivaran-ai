import pytest

from app.brain import llm
from app.brain.llm import simplify_schema
from app.config import ConfigError, get_settings
from app.models.case import UnderstandOutput


def test_simplified_schema_has_no_refs_or_titles():
    s = simplify_schema(UnderstandOutput.model_json_schema())
    text = str(s)
    assert "$ref" not in text and "$defs" not in text and "'title'" not in text
    assert s["additionalProperties"] is False
    assert "food_delivery" in text  # enums survived the inlining


def test_gemini_is_the_default_provider(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    assert get_settings().provider == "gemini"


def test_provider_can_be_switched_to_claude(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    assert get_settings().provider == "anthropic"


def test_unknown_provider_is_rejected(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "banana")
    with pytest.raises(ConfigError):
        get_settings()


def test_missing_key_gives_a_clear_error(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    with pytest.raises(ConfigError, match="GEMINI_API_KEY"):
        llm.make_llm()


def test_rpm_setting_is_read_from_env(monkeypatch):
    monkeypatch.setenv("GEMINI_RPM", "3")
    monkeypatch.setenv("GEMINI_RPD", "20")
    s = get_settings()
    assert (s.gemini_rpm, s.gemini_rpd) == (3, 20)
