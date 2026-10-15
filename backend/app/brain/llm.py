"""Claude wrapper. Everything else talks to the LLMClient interface, so tests can use a fake."""
import json
from typing import Protocol

import anthropic

from app.config import get_settings


class LLMError(RuntimeError):
    pass


class LLMClient(Protocol):
    def complete_json(self, *, system: str, user: str, schema: dict) -> dict: ...


class AnthropicLLM:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

    def complete_json(self, *, system: str, user: str, schema: dict) -> dict:
        output_config: dict = {"format": {"type": "json_schema", "schema": schema}}
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


def schema_for(model_cls: type) -> dict:
    """JSON schema in the shape Claude's structured output accepts."""
    return anthropic.transform_schema(model_cls)
