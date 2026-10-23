"""Groq's free Whisper as a speech-to-text provider (no card needed). Key in GROQ_API_KEY."""
import os

from app.brain.ratelimit import RateLimiter
from app.config import ConfigError, get_settings
from app.speech.base import SpeechError, Transcript

URL = "https://api.groq.com/openai/v1/audio/transcriptions"
# our language hints -> Whisper's two-letter codes. "auto" and "hinglish" let Whisper decide; the prompt steers the script.
CODES = {"en-IN": "en", "hi-IN": "hi", "ta-IN": "ta"}
PROMPT = {
    "hinglish": "Hindi and English mixed, written in English letters: mera order Swiggy se aaya, mujhe refund chahiye.",
    "auto": "Customer care call in India. Hindi, English, Tamil or mixed. Companies: Swiggy, Zomato, Amazon, Myntra, IRCTC, Airtel.",
}


class GroqSTT:
    def __init__(self, limiter: RateLimiter | None = None) -> None:
        s = get_settings()
        self._s = s
        self._key = os.getenv("GROQ_API_KEY", "").strip()
        if not self._key:
            raise ConfigError("GROQ_API_KEY is not set. Add it to .env.")
        self._limiter = limiter or RateLimiter(s.groq_stt_rpm, 0)

    def transcribe(self, audio: bytes, mime_type: str, language: str | None = None) -> Transcript:
        import httpx

        self._limiter.acquire()
        data = {"model": self._s.groq_stt_model, "temperature": "0", "response_format": "json"}
        if language in CODES:
            data["language"] = CODES[language]
        if language in PROMPT:
            data["prompt"] = PROMPT[language]
        try:
            r = httpx.post(URL, data=data, files={"file": ("audio.wav", audio, mime_type)},
                           headers={"Authorization": f"Bearer {self._key}"}, timeout=30)
        except httpx.HTTPError as e:
            raise SpeechError(f"Groq speech-to-text did not answer ({type(e).__name__}).") from e
        if r.status_code != 200:
            raise SpeechError(f"Groq speech-to-text error {r.status_code}.")
        try:
            text = (r.json().get("text") or "").strip()
        except ValueError as e:
            raise SpeechError("Groq speech-to-text returned an unusable answer.") from e
        return Transcript(text=text, language=CODES.get(language) and language, provider="groq")
