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
    BUSY_WAITS = (10, 20, 40, 60)  # seconds to wait after a 5xx 'server busy' answer

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


def make_llm() -> LLMClient:
    provider = get_settings().provider
    try:
        return GeminiLLM() if provider == "gemini" else AnthropicLLM()
    except ConfigError:
        raise
    except Exception as e:  # a missing API key shows up here
        key = "GEMINI_API_KEY" if provider == "gemini" else "ANTHROPIC_API_KEY"
        raise ConfigError(f"Could not start the {provider} client. Is {key} set in .env? ({e})") from e
