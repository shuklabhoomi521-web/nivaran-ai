"""A small in-memory log of what the bot heard and said, shown on the voice test page. No audio is ever stored here."""
import time

EVENTS: list[dict] = []


def log_event(kind: str, text: str, **extra) -> None:
    EVENTS.append({"n": (EVENTS[-1]["n"] + 1) if EVENTS else 1, "t": time.strftime("%H:%M:%S"), "kind": kind, "text": text, **extra})
    del EVENTS[:-200]
