"""Sarvam AI speech providers (made for Indian languages). Free sign-up credits: Rs 100 (their pricing page); a card may or
may not be needed (not stated). Key: SARVAM_API_KEY in .env, created at https://dashboard.sarvam.ai"""
import base64
import os
import re
import time
from pathlib import Path

from app.brain.ratelimit import DailyQuotaExceeded, RateLimiter
from app.config import ConfigError, get_settings
from app.speech.base import SpeechAudio, SpeechError, Transcript
from app.speech.gemini import BUSY_WAITS, HardTimeout, _run_with_hard_timeout

USAGE_FILE = Path(__file__).resolve().parents[3] / ".sarvam_usage.json"   # git-ignored


def _client():
    from sarvamai import SarvamAI

    key = os.getenv("SARVAM_API_KEY", "").strip()
    if not key:
        raise ConfigError("SARVAM_API_KEY is not set. Create a key at https://dashboard.sarvam.ai and add it to .env.")
    return SarvamAI(api_subscription_key=key)


def _call(limiter: RateLimiter, fn, what: str, hard_timeout: float = 75):
    for attempt in range(len(BUSY_WAITS) + 1):
        try:
            limiter.acquire()
            return _run_with_hard_timeout(fn, hard_timeout)
        except DailyQuotaExceeded:
            raise
        except HardTimeout as e:
            if attempt < 2:
                time.sleep(BUSY_WAITS[attempt])
                continue
            raise SpeechError(f"Sarvam {what} timed out") from e
        except Exception as e:  # noqa: BLE001
            code = getattr(e, "status_code", None)
            msg = str(e)
            if code == 429 and attempt < len(BUSY_WAITS):
                time.sleep(BUSY_WAITS[attempt] + 5)
                continue
            if code in (500, 502, 503, 504) and attempt < len(BUSY_WAITS):
                time.sleep(BUSY_WAITS[attempt])
                continue
            if code in (401, 403):
                raise SpeechError(f"Sarvam rejected the key ({code}). Check SARVAM_API_KEY.") from e
            if code == 402 or re.search(r"insufficient|credit|balance|quota", msg, re.I):
                raise DailyQuotaExceeded(f"Sarvam credits look used up ({what}): {msg[:120]}") from e
            raise SpeechError(f"Sarvam {what} error {code}: {msg[:160]}") from e
    raise SpeechError(f"Sarvam {what} failed after several tries.")


class SarvamSTT:
    # Our language hints -> Sarvam language code and output style. "transcribe" keeps each language's own script;
    # "translit" writes everything in English letters (what Hinglish users type).
    HINTS = {"hi-IN": ("hi-IN", "transcribe"), "ta-IN": ("ta-IN", "transcribe"), "en-IN": ("en-IN", "transcribe"),
             "hinglish": ("hi-IN", "translit")}

    def __init__(self, client=None, limiter: RateLimiter | None = None) -> None:
        s = get_settings()
        self._s = s
        self._client = client or _client()
        self._limiter = limiter or RateLimiter(s.sarvam_rpm, 0, usage_file=USAGE_FILE)

    def transcribe(self, audio: bytes, mime_type: str, language: str | None = None) -> Transcript:
        code, mode = self.HINTS.get(language, ("unknown", "transcribe"))
        kwargs = dict(file=("audio.wav", audio, mime_type), model=self._s.sarvam_stt_model, language_code=code,
                      mode=mode, input_audio_codec="wav")
        r = _call(self._limiter, lambda: self._client.speech_to_text.transcribe(**kwargs), "speech-to-text")
        return Transcript(text=(r.transcript or "").strip(), language=getattr(r, "language_code", None) or code)


class SarvamTTS:
    SPEAKERS = {"hi-IN": "ritu_hi_customer", "ta-IN": "gokul_ta_narration", "en-IN": "simran_en_customer"}

    def __init__(self, client=None, limiter: RateLimiter | None = None) -> None:
        s = get_settings()
        self._s = s
        self._client = client or _client()
        self._limiter = limiter or RateLimiter(s.sarvam_rpm, 0, usage_file=USAGE_FILE)

    def synthesize(self, text: str, language: str | None = None, voice: str | None = None,
                   codec: str = "wav", sample_rate: int = 24000) -> SpeechAudio:
        """codec 'mulaw' with sample_rate 8000 gives audio that can go straight down a phone line (Phase 4)."""
        code = language or "en-IN"
        kwargs = dict(text=text, language_code=code, speaker=voice or self.SPEAKERS.get(code, "simran_en_customer"),
                      model=self._s.sarvam_tts_model, output_audio_codec=codec, speech_sample_rate=sample_rate)
        r = _call(self._limiter, lambda: self._client.text_to_speech.convert(**kwargs), "text-to-speech")
        if not r.audios:
            raise SpeechError("Sarvam returned no audio.")
        data = b"".join(base64.b64decode(a) for a in r.audios)
        return SpeechAudio(data=data, mime_type="audio/wav" if codec == "wav" else f"audio/{codec}", sample_rate=sample_rate)
