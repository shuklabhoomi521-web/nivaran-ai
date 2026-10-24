"""Streaming helpers: speak the first sentence of an answer while the AI is still writing the rest.
The AI writes JSON such as {"action": "continue", "digits": "", "say": "Hello. How are you?"}. We read the text as it arrives, find the
value of the "say" field and cut it into sentences as soon as each one is complete."""
import json
import re

_SENTENCE_END = re.compile(r"(?<=[.!?।])\s+")
_ACTION = re.compile(r'"action"\s*:\s*"(\w+)"')


class SayStreamer:
    """Feed it the raw JSON text piece by piece; it hands back complete sentences of the `say` field (and knows the `action`)."""

    def __init__(self, key: str = "say") -> None:
        self._key = re.compile(r'"%s"\s*:\s*"' % re.escape(key))
        self.text = ""              # everything received so far
        self._read = None           # index in self.text of the next unread character of the string (None until the string starts)
        self._raw = ""              # the string so far, still with escapes
        self._pending = ""          # decoded text not yet handed out
        self.closed = False         # the closing quote has arrived
        self.action: str | None = None

    def feed(self, chunk: str) -> list[str]:
        self.text += chunk
        if self.action is None:
            m = _ACTION.search(self.text)
            self.action = m.group(1) if m else None
        if self._read is None:
            m = self._key.search(self.text)
            if not m:
                return []
            self._read = m.end()
        out: list[str] = []
        i = self._read
        while i < len(self.text) and not self.closed:
            c = self.text[i]
            if c == "\\":
                if i + 1 >= len(self.text):
                    break                                       # an escape is cut in half: wait for the next piece
                if self.text[i + 1] == "u" and i + 5 >= len(self.text):
                    break
                esc = self.text[i + 1]
                if esc == "u":
                    self._pending += chr(int(self.text[i + 2:i + 6], 16)); i += 6
                else:
                    self._pending += {"n": " ", "t": " ", "r": " ", "b": "", "f": ""}.get(esc, esc); i += 2
            elif c == '"':
                self.closed = True; i += 1
            else:
                self._pending += c; i += 1
        self._read = i
        parts = _SENTENCE_END.split(self._pending)
        if len(parts) > 1:                                      # everything but the last piece is a finished sentence
            out = [p.strip() for p in parts[:-1] if p.strip()]
            self._pending = parts[-1]
        if self.closed and self._pending.strip():
            out.append(self._pending.strip()); self._pending = ""
        return out

    def flush(self) -> list[str]:
        """The stream ended: hand out what is left (only if the string was complete)."""
        rest = self._pending.strip() if self.closed else ""
        self._pending = ""
        return [rest] if rest else []

    def full_json(self) -> dict:
        return json.loads(self.text)
