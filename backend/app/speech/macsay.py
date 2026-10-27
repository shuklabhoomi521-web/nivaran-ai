"""Free text-to-speech from the Mac's own voices (the `say` command). For DEVELOPMENT and practice runs only: instant, costs nothing,
sounds robotic. Real calls and the demo use Sarvam's voice."""
import subprocess
import tempfile
import wave
from pathlib import Path

from app.speech.base import SpeechAudio, SpeechError

VOICES = {"en-IN": "Rishi", "hi-IN": "Lekha", "ta-IN": "Vani", "hinglish": "Lekha"}


class MacSayTTS:
    def synthesize(self, text: str, language: str | None = None, voice: str | None = None) -> SpeechAudio:
        v = voice or VOICES.get(language or "en-IN", "Samantha")
        try:
            with tempfile.TemporaryDirectory() as t:
                aiff, out = Path(t) / "a.aiff", Path(t) / "a.wav"
                subprocess.run(["say", "-v", v, "-o", str(aiff), text], check=True, timeout=30, capture_output=True)
                subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16@24000", "-c", "1", str(aiff), str(out)], check=True, timeout=30, capture_output=True)
                with wave.open(str(out)) as w:
                    rate = w.getframerate()
                return SpeechAudio(data=out.read_bytes(), mime_type="audio/wav", sample_rate=rate, provider="mac")
        except (subprocess.SubprocessError, OSError) as e:
            raise SpeechError(f"Mac voice failed: {type(e).__name__}") from e
