"""LLM wrappers. Everything else talks to the LLMClient interface, so tests can use a fake.

Default provider is Gemini (free tier). Set LLM_PROVIDER=anthropic in .env to use Claude.
"""
import json
import re
import time
from typing import Protocol

from app.brain.ratelimit import DailyQuotaExceeded, RateLimiter
from app.config import ConfigError, get_settings


class LLMError(RuntimeError):
    pass


class LLMClient(Protocol):
    def complete_json(self, *, system: str, user: str, schema: dict) -> dict: ...


def simplify_schema(schema: dict) -> dict:
    """Inline $ref pointers and drop 'title' keys: the plainest JSON schema Gemini accepts."""
    defs = schema.get("$defs", {})

    def walk(node):
        if isinstance(node, list):
            return [walk(x) for x in node]
        if not isinstance(node, dict):
            return node
        if "$ref" in node:
            return walk(defs[node["$ref"].split("/")[-1]])
        return {k: walk(v) for k, v in node.items() if k not in ("$defs", "title")}

    return walk(schema)


class GeminiLLM:
    MAX_RETRIES = 4
    HARD_TIMEOUT = 25      # seconds before we give up on one text call
    BUSY_WAITS = (2, 5, 10, 20)  # seconds to wait after a 5xx 'server busy' answer

    def __init__(self, limiter: RateLimiter | None = None) -> None:
        from google import genai  # imported here so Claude-only setups do not need it

        self._settings = get_settings()
        self._client = genai.Client()  # reads GEMINI_API_KEY from the environment
        self._limiter = limiter or RateLimiter(self._settings.gemini_rpm, self._settings.gemini_rpd)

    def _ask(self, user: str, config):
        """Ask the main model; if it has not answered within a few seconds, ALSO ask the backup model and take whichever answers first.
        (The free tier is sometimes very slow on one model and fast on another; a live voice chat cannot wait 15 seconds.)"""
        import queue
        import threading

        from app.speech.gemini import HardTimeout
        s = self._settings
        models = [s.gemini_model]
        if s.gemini_backup_model not in ("none", s.gemini_model) and s.gemini_hedge_seconds > 0:
            models.append(s.gemini_backup_model)
        results: queue.Queue = queue.Queue()

        def run(model: str):
            try:
                results.put(("ok", self._client.models.generate_content(model=model, contents=user, config=config)))
            except Exception as e:  # noqa: BLE001
                results.put(("err", e))

        launched, errors, deadline = 0, [], time.time() + self.HARD_TIMEOUT

        def launch():
            nonlocal launched
            threading.Thread(target=run, args=(models[launched],), daemon=True).start()
            launched += 1

        launch()
        while True:
            remaining = deadline - time.time()
            wait = min(s.gemini_hedge_seconds, remaining) if launched < len(models) else remaining
            try:
                kind, value = results.get(timeout=max(0.0, wait))
            except queue.Empty:
                if launched < len(models) and remaining > 0:
                    launch()                      # the main model is slow: also ask the backup
                    continue
                raise HardTimeout(f"no answer after {self.HARD_TIMEOUT}s")
            if kind == "ok":
                return value
            errors.append(value)
            if launched < len(models):
                launch()                          # the main model failed: ask the backup right away
            elif len(errors) >= launched:
                raise errors[-1]

    def complete_json(self, *, system: str, user: str, schema: dict) -> dict:
        from google.genai import errors, types

        config = types.GenerateContentConfig(
            system_instruction=system,
            response_mime_type="application/json",
            response_json_schema=simplify_schema(schema),
        )
        from app.speech.gemini import HardTimeout, _run_with_hard_timeout     # same "give up on a hung call" helper as speech

        for attempt in range(self.MAX_RETRIES + 1):
            try:
                self._limiter.acquire()
                response = self._ask(user, config)
                break
            except HardTimeout as e:     # a hung answer: try again once, then fail clearly (a live voice chat cannot wait minutes)
                if attempt < 1:
                    continue
                raise LLMError("Gemini did not answer in time.") from e
            except DailyQuotaExceeded:
                raise
            except errors.APIError as e:
                if e.code == 429:
                    text = str(e)
                    if re.search(r"PerDay|per day|daily", text, re.I):
                        raise DailyQuotaExceeded("Gemini daily free limit reached.") from e
                    if attempt < self.MAX_RETRIES:
                        m = re.search(r"retry in ([\d.]+)s", text, re.I)
                        time.sleep(float(m.group(1)) + 1 if m else 30)
                        continue
                    raise LLMError("Gemini is rate limiting us. Try again in a minute.") from e
                if e.code in (500, 502, 503, 504):  # Google is busy: wait and try again
                    if attempt < self.MAX_RETRIES:
                        time.sleep(self.BUSY_WAITS[min(attempt, len(self.BUSY_WAITS) - 1)])
                        continue
                    raise LLMError("Gemini is busy right now. Try again in a few minutes.") from e
                raise LLMError(f"Gemini error {e.code}: {e.message}") from e
        text = response.text
        if not text:
            raise LLMError("Gemini returned no text (blocked or empty).")
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise LLMError("Gemini returned invalid JSON.") from e


class AnthropicLLM:
    def __init__(self) -> None:
        import anthropic

        self._settings = get_settings()
        if not self._settings.claude_model:
            raise ConfigError("CLAUDE_MODEL is not set. Add it to .env (see .env.example).")
        self._client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

    def complete_json(self, *, system: str, user: str, schema: dict) -> dict:
        import anthropic

        output_config: dict = {"format": {"type": "json_schema", "schema": anthropic.transform_schema(schema)}}
        if self._settings.claude_effort:
            output_config["effort"] = self._settings.claude_effort
        response = self._client.messages.create(
            model=self._settings.claude_model,
            max_tokens=8000,
            system=system,
            messages=[{"role": "user", "content": user}],
            output_config=output_config,
        )
        if response.stop_reason == "refusal":
            raise LLMError("The AI declined this request.")
        if response.stop_reason == "max_tokens":
            raise LLMError("The AI answer was cut off.")
        text = next((b.text for b in response.content if b.type == "text"), None)
        if text is None:
            raise LLMError("The AI returned no text.")
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise LLMError("The AI returned invalid JSON.") from e


class GroqLLM:
    """Groq's free tier (no card): very fast open models. OpenAI-style web API, key in GROQ_API_KEY."""

    URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, limiter: RateLimiter | None = None) -> None:
        import os

        self._settings = get_settings()
        self._key = os.getenv("GROQ_API_KEY", "").strip()
        if not self._key:
            raise ConfigError("GROQ_API_KEY is not set. Add it to .env.")
        self._limiter = limiter or RateLimiter(self._settings.groq_rpm, 0)

    def complete_json(self, *, system: str, user: str, schema: dict) -> dict:
        import httpx

        self._limiter.acquire()
        schema = simplify_schema(schema)
        body = {
            "model": self._settings.groq_model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "response_format": {"type": "json_schema", "json_schema": {"name": "answer", "schema": schema}},
            "temperature": 0.2,
            "max_completion_tokens": 1500,
        }
        if "gpt-oss" in self._settings.groq_model:
            body["reasoning_effort"] = "low"
        try:
            r = httpx.post(self.URL, json=body, headers={"Authorization": f"Bearer {self._key}"}, timeout=self._settings.groq_timeout)
        except httpx.HTTPError as e:
            raise LLMError(f"Groq did not answer ({type(e).__name__}).") from e
        if r.status_code != 200:
            raise LLMError(f"Groq error {r.status_code}.")
        try:
            return json.loads(r.json()["choices"][0]["message"]["content"])
        except (KeyError, IndexError, ValueError, TypeError) as e:
            raise LLMError("Groq returned an unusable answer.") from e


    def stream_json(self, *, system: str, user: str, schema: dict):
        """Like complete_json, but yields the raw JSON text piece by piece as the AI writes it (so we can start speaking early)."""
        import httpx

        self._limiter.acquire()
        body = {
            "model": self._settings.groq_model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "response_format": {"type": "json_schema", "json_schema": {"name": "answer", "schema": simplify_schema(schema)}},
            "temperature": 0.2, "max_completion_tokens": 1500, "stream": True,
        }
        if "gpt-oss" in self._settings.groq_model:
            body["reasoning_effort"] = "low"
        try:
            with httpx.stream("POST", self.URL, json=body, headers={"Authorization": f"Bearer {self._key}"}, timeout=self._settings.groq_timeout) as r:
                if r.status_code != 200:
                    raise LLMError(f"Groq error {r.status_code}.")
                for line in r.iter_lines():
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        return
                    try:
                        piece = json.loads(data)["choices"][0]["delta"].get("content")
                    except (ValueError, KeyError, IndexError):
                        continue
                    if piece:
                        yield piece
        except httpx.HTTPError as e:
            raise LLMError(f"Groq did not answer ({type(e).__name__}).") from e


class FallbackLLM:
    """Ask the fast main AI; if it fails or is slow, ask the backup. (Groq first, Gemini as backup.)"""

    def __init__(self, primary: LLMClient, backup: LLMClient) -> None:
        self.primary, self.backup, self.last_used = primary, backup, "primary"

    def complete_json(self, *, system: str, user: str, schema: dict) -> dict:
        try:
            out = self.primary.complete_json(system=system, user=user, schema=schema)
            self.last_used = "primary"
            return out
        except Exception:  # noqa: BLE001 - any failure of the fast AI: use the backup
            self.last_used = "backup"
            return self.backup.complete_json(system=system, user=user, schema=schema)

    def stream_json(self, *, system: str, user: str, schema: dict):
        """Stream from the fast AI. If it fails BEFORE the first piece, the backup answers in one piece; if it fails midway we raise
        (a half-spoken answer cannot be taken back)."""
        started = False
        try:
            for piece in self.primary.stream_json(system=system, user=user, schema=schema):
                started = True
                yield piece
            self.last_used = "primary"
            return
        except Exception:  # noqa: BLE001
            if started:
                raise
        self.last_used = "backup"
        yield json.dumps(self.backup.complete_json(system=system, user=user, schema=schema), ensure_ascii=False)


def make_llm() -> LLMClient:
    provider = get_settings().provider
    try:
        if provider == "groq":
            return FallbackLLM(GroqLLM(), GeminiLLM())
        return GeminiLLM() if provider == "gemini" else AnthropicLLM()
    except ConfigError:
        raise
    except Exception as e:  # a missing API key shows up here
        key = "GEMINI_API_KEY" if provider == "gemini" else "ANTHROPIC_API_KEY"
        raise ConfigError(f"Could not start the {provider} client. Is {key} set in .env? ({e})") from e
