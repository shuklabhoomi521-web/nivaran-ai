"""Gemini speech providers (free tier). Same slow-down as the text brain: our own requests-per-minute
and per-day limits, retries on 'server busy', and a clean stop on a daily 429."""
import base64
import re
import time
from pathlib import Path

from app.brain.ratelimit import DailyQuotaExceeded, RateLimiter
from app.config import get_settings
from app.speech.base import SpeechAudio, SpeechError, Transcript

SPEECH_USAGE_FILE = Path(__file__).resolve().parents[3] / ".speech_usage.json"   # git-ignored
BUSY_WAITS = (10, 20, 40, 60)


def _call_with_retries(limiter: RateLimiter, fn, what: str):
    from google.genai import errors

    for attempt in range(len(BUSY_WAITS) + 1):
        try:
            limiter.acquire()
            return fn()
        except DailyQuotaExceeded:
            raise
        except errors.APIError as e:
            text = str(e)
            if e.code == 429:
                if re.search(r"PerDay|per day|daily", text, re.I):
                    raise DailyQuotaExceeded(f"Gemini daily free limit reached ({what}).") from e
                m = re.search(r"retry in ([\d.]+)s", text, re.I)
                if attempt < len(BUSY_WAITS):
                    time.sleep(float(m.group(1)) + 1 if m else 30)
                    continue
                raise SpeechError(f"Gemini is rate limiting us ({what}).") from e
            if e.code in (500, 502, 503, 504) and attempt < len(BUSY_WAITS):
                time.sleep(BUSY_WAITS[attempt])
                continue
            raise SpeechError(f"Gemini {what} error {e.code}: {e.message}") from e


def make_limiter() -> RateLimiter:
    s = get_settings()
    return RateLimiter(s.speech_rpm, s.speech_rpd, usage_file=SPEECH_USAGE_FILE)


class GeminiSTT:
    def __init__(self, limiter: RateLimiter | None = None) -> None:
        from google import genai

        self._s = get_settings()
        self._client = genai.Client()
        self._limiter = limiter or make_limiter()

    def transcribe(self, audio: bytes, mime_type: str, language: str | None = None) -> Transcript:
        cfg: dict = {}
        if language:
            cfg["transcription_config"] = {"language_codes": [language]}
        body = dict(
            model=self._s.gemini_stt_model,
            input=[{"type": "audio", "data": base64.b64encode(audio).decode(), "mime_type": mime_type}],
        )
        if cfg:
            body["generation_config"] = cfg
        it = _call_with_retries(self._limiter, lambda: self._client.interactions.create(**body), "speech-to-text")
        text = (it.output_text or "").strip()
        return Transcript(text=text, language=language)


class GeminiTTS:
    def __init__(self, limiter: RateLimiter | None = None) -> None:
        from google import genai

        self._s = get_settings()
        self._client = genai.Client()
        self._limiter = limiter or make_limiter()

    def synthesize(self, text: str, language: str | None = None, voice: str | None = None) -> SpeechAudio:
        speech: dict = {"voice": voice or self._s.gemini_tts_voice}
        if language:
            speech["language"] = language
        body = dict(model=self._s.gemini_tts_model, input=text, response_format={"type": "audio"},
                    generation_config={"speech_config": [speech]})
        it = _call_with_retries(self._limiter, lambda: self._client.interactions.create(**body), "text-to-speech")
        audio = it.output_audio
        if audio is None or not audio.data:
            raise SpeechError("Gemini returned no audio.")
        return SpeechAudio(data=base64.b64decode(audio.data), mime_type="audio/wav", sample_rate=24000)
