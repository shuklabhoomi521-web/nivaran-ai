"""Fake providers for free tests: no network, no keys."""
from app.speech.base import SpeechAudio, Transcript


class FakeSTT:
    def __init__(self, text: str = "hello"):
        self.text, self.calls = text, []

    def transcribe(self, audio: bytes, mime_type: str, language: str | None = None) -> Transcript:
        self.calls.append((len(audio), mime_type, language))
        return Transcript(text=self.text, language=language)


class FakeTTS:
    def __init__(self):
        self.calls = []

    def synthesize(self, text: str, language: str | None = None, voice: str | None = None) -> SpeechAudio:
        self.calls.append((text, language, voice))
        return SpeechAudio(data=b"RIFF....WAVEfake", mime_type="audio/wav", sample_rate=24000)
