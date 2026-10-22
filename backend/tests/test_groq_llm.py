import httpx
import pytest

from app.brain.llm import FallbackLLM, GroqLLM, LLMError


class Boom:
    def complete_json(self, **kw):
        raise LLMError("down")


class Ok:
    def complete_json(self, **kw):
        return {"a": 1}


def test_backup_answers_when_the_fast_ai_fails():
    f = FallbackLLM(Boom(), Ok())
    assert f.complete_json(system="s", user="u", schema={}) == {"a": 1} and f.last_used == "backup"


def test_backup_is_not_used_when_the_fast_ai_works():
    f = FallbackLLM(Ok(), Boom())
    assert f.complete_json(system="s", user="u", schema={}) == {"a": 1} and f.last_used == "primary"


def _groq(monkeypatch, response):
    monkeypatch.setenv("GROQ_API_KEY", "test-key-not-real")
    seen = {}

    def post(url, json, headers, timeout):
        seen.update(url=url, body=json, timeout=timeout)
        if isinstance(response, Exception):
            raise response
        return response
    monkeypatch.setattr(httpx, "post", post)
    return GroqLLM(), seen


def test_groq_sends_the_schema_and_returns_the_json(monkeypatch):
    r = httpx.Response(200, json={"choices": [{"message": {"content": '{"x": 2}'}}]})
    g, seen = _groq(monkeypatch, r)
    assert g.complete_json(system="s", user="u", schema={"type": "object"}) == {"x": 2}
    assert seen["body"]["response_format"]["type"] == "json_schema" and seen["url"].startswith("https://api.groq.com/")


@pytest.mark.parametrize("resp", [httpx.Response(429, json={}), httpx.Response(200, json={"choices": []}), httpx.ConnectTimeout("slow")])
def test_groq_problems_become_llm_errors_so_the_backup_can_take_over(monkeypatch, resp):
    g, _ = _groq(monkeypatch, resp)
    with pytest.raises(LLMError):
        g.complete_json(system="s", user="u", schema={})
