"""Gemini speech providers (free tier). Same slow-down as the text brain: our own requests-per-minute
and per-day limits, retries on 'server busy', and a clean stop on a daily 429."""
import base64
import re
import threading
import time

import httpx
from pathlib import Path

from app.brain.ratelimit import DailyQuotaExceeded, RateLimiter
from app.config import get_settings
from app.speech.base import SpeechAudio, SpeechError, Transcript

SPEECH_USAGE_FILE = Path(__file__).resolve().parents[3] / ".speech_usage.json"   # git-ignored
BUSY_WAITS = (10, 20, 40, 60)


class HardTimeout(Exception):
    pass


def _run_with_hard_timeout(fn, seconds: float):
    """Google's own timeout setting did not stop a hung audio call, so we run the call in a daemon
    thread and give up after `seconds` (the hung thread is left behind and never blocks exit)."""
    box: dict = {}

    def target():
        try:
            box["value"] = fn()
        except BaseException as e:  # noqa: BLE001 - re-raised in the caller
            box["error"] = e

    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(seconds)
    if t.is_alive():
        raise HardTimeout(f"no answer after {seconds:.0f}s")
    if "error" in box:
        raise box["error"]
    return box["value"]


def _call_with_retries(limiter: RateLimiter, fn, what: str, hard_timeout: float = 75):
    from google.genai import errors

    for attempt in range(len(BUSY_WAITS) + 1):
        try:
            limiter.acquire()
            return _run_with_hard_timeout(fn, hard_timeout)
        except DailyQuotaExceeded:
            raise
        except (httpx.TimeoutException, httpx.NetworkError, HardTimeout) as e:   # hung or dropped connection (for example after the laptop slept)
            if attempt < 2:    # a hung call is retried twice, not forever
                time.sleep(BUSY_WAITS[attempt])
                continue
            raise SpeechError(f"Gemini {what} timed out: {type(e).__name__}") from e
        except Exception as e:  # noqa: BLE001
            # the Google SDK has its own timeout/connection error classes (not httpx's): treat them like a hung call
            if type(e).__name__ in ("APITimeoutError", "APIConnectionError"):
                if attempt < 2:
                    time.sleep(BUSY_WAITS[attempt])
                    continue
                raise SpeechError(f"Gemini {what} timed out: {type(e).__name__}") from e
            if not isinstance(e, errors.APIError):
                raise
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
    raise SpeechError(f"Gemini {what} failed after several tries.")


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
        if language and "-" in language:     # a real language code such as hi-IN (not our "hinglish" label)
            cfg["transcription_config"] = {"language_codes": [language]}
        body = dict(
            model=self._s.gemini_stt_model,
            input=[{"type": "audio", "data": base64.b64encode(audio).decode(), "mime_type": mime_type}],
        )
        if cfg:
            body["generation_config"] = cfg
        it = _call_with_retries(self._limiter, lambda: self._client.interactions.create(timeout=60, **body), "speech-to-text")
        text = (it.output_text or "").strip()
        return Transcript(text=text, language=language)


class GeminiPromptSTT:
    """Transcription with a general Gemini model and a plain instruction. Used when the dedicated transcribe model
    is slow or overloaded, and as a second opinion in the bake-off."""

    PROMPT = ("Transcribe this audio exactly as spoken, word for word. Keep the original language and script "
              "(Devanagari for Hindi, Tamil script for Tamil, English letters for English). If the speaker mixes Hindi and "
              "English, keep each word in the language it was spoken. Do not translate, summarise or add anything. "
              "Output only the transcript.")

    # The app knows the language the user picked, so we tell the model. Without this it sometimes
    # wrote Hindi in English letters or answered a Tamil clip in Hindi.
    HINTS = {
        "hi-IN": "The speaker is speaking Hindi. Write the transcript in Devanagari script.",
        "ta-IN": "The speaker is speaking Tamil. Write the transcript in Tamil script.",
        "en-IN": "The speaker is speaking English (Indian accent). Write the transcript in English letters.",
        "hinglish": "The speaker mixes Hindi and English (Hinglish). Write Hindi words in English letters and English words normally.",
    }

    def __init__(self, limiter: RateLimiter | None = None) -> None:
        from google import genai

        self._s = get_settings()
        self._client = genai.Client()
        self._limiter = limiter or make_limiter()

    def transcribe(self, audio: bytes, mime_type: str, language: str | None = None) -> Transcript:
        prompt = self.PROMPT + (" " + self.HINTS[language] if language in self.HINTS else "")
        body = dict(
            model=self._s.gemini_prompt_stt_model,
            input=[{"type": "audio", "data": base64.b64encode(audio).decode(), "mime_type": mime_type},
                   {"type": "text", "text": prompt}],
        )
        it = _call_with_retries(self._limiter, lambda: self._client.interactions.create(timeout=60, **body), "speech-to-text (prompt)")
        return Transcript(text=(it.output_text or "").strip(), language=language)


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
        it = _call_with_retries(self._limiter, lambda: self._client.interactions.create(timeout=90, **body), "text-to-speech")
        audio = it.output_audio
        if audio is None or not audio.data:
            raise SpeechError("Gemini returned no audio.")
        return SpeechAudio(data=base64.b64decode(audio.data), mime_type="audio/wav", sample_rate=24000)
