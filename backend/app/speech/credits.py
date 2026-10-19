"""Sarvam credit tracking. Sarvam gives new accounts Rs 100 of free credit, then charges: speech-to-text Rs 30 per hour of audio
(billed per second), text-to-speech Rs 2 per 1,000 characters on bulbul:v4-flash (Rs 3 on v3). We have no official balance
check, so we keep our own ledger of what we send. It is an ESTIMATE: compare with the Sarvam dashboard now and then."""
import json
import wave
from io import BytesIO
from pathlib import Path

from app.config import get_settings

LEDGER_FILE = Path(__file__).resolve().parents[3] / ".sarvam_credits.json"      # git-ignored
STT_RUPEES_PER_SECOND = 30 / 3600
TTS_RUPEES_PER_CHAR = {"bulbul:v4-flash": 2 / 1000, "bulbul:v3": 3 / 1000, "bulbul:v2": 3 / 1000}
LOW, CRITICAL, EMPTY = 25.0, 10.0, 2.0     # rupees left: below these we warn, warn loudly, and stop using Sarvam


def wav_seconds(audio: bytes) -> float:
    try:
        with wave.open(BytesIO(audio), "rb") as w:
            return w.getnframes() / float(w.getframerate())
    except Exception:  # noqa: BLE001 - not a plain wav: assume 16 kHz mono 16-bit
        return len(audio) / 32000.0


class CreditLedger:
    def __init__(self, file: Path = LEDGER_FILE) -> None:
        self.file = file
        s = get_settings()
        self._start = s.sarvam_credit_rupees
        self._seed = s.sarvam_credit_already_spent
        self._tts_rate = TTS_RUPEES_PER_CHAR.get(s.sarvam_tts_model, 3 / 1000)

    def _read(self) -> dict:
        try:
            return json.loads(self.file.read_text())
        except (OSError, ValueError):
            return {"stt_seconds": 0.0, "tts_chars": 0, "seed_spent": self._seed, "warned": "ok"}

    def _write(self, d: dict) -> None:
        try:
            self.file.write_text(json.dumps(d))
        except OSError:
            pass

    def add_stt(self, audio: bytes) -> None:
        d = self._read()
        d["stt_seconds"] += wav_seconds(audio)
        self._write(d)

    def add_tts(self, chars: int) -> None:
        d = self._read()
        d["tts_chars"] += chars
        self._write(d)

    def spent(self) -> float:
        d = self._read()
        return d["seed_spent"] + d["stt_seconds"] * STT_RUPEES_PER_SECOND + d["tts_chars"] * self._tts_rate

    def remaining(self) -> float:
        return max(0.0, self._start - self.spent())

    def level(self) -> str:
        r = self.remaining()
        return "empty" if r <= EMPTY else "critical" if r <= CRITICAL else "low" if r <= LOW else "ok"

    def minutes_left(self) -> float:
        return self.remaining() / STT_RUPEES_PER_SECOND / 60

    def message(self) -> str | None:
        lv = self.level()
        if lv == "ok":
            return None
        if lv == "empty":
            return "Sarvam credit is used up (estimate). Speech now goes to the Gemini backup."
        return (f"Sarvam credit is {lv}: about Rs {self.remaining():.0f} left, roughly {self.minutes_left():.0f} minutes of speech-to-text. "
                "Check the Sarvam dashboard.")

    def warn_once(self) -> str | None:
        """Return a warning only when the level gets worse (so logs are not flooded)."""
        d, lv = self._read(), self.level()
        order = ["ok", "low", "critical", "empty"]
        if order.index(lv) > order.index(d.get("warned", "ok")):
            d["warned"] = lv
            self._write(d)
            return self.message()
        return None

    def summary(self) -> str:
        return (f"Sarvam credit (estimate): started Rs {self._start:.0f}, spent about Rs {self.spent():.1f}, "
                f"about Rs {self.remaining():.1f} left (~{self.minutes_left():.0f} min of speech-to-text); level: {self.level()}")
