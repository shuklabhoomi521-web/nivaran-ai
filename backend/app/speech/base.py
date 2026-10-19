"""Speech interfaces. Providers (Gemini now; Sarvam or our own models later) plug in behind these,
so the voice pipeline never depends on one vendor."""
from dataclasses import dataclass
from typing import Protocol


class SpeechError(RuntimeError):
    pass


@dataclass
class Transcript:
    text: str
    language: str | None = None
    provider: str | None = None      # which provider really answered (matters when a backup stepped in)


@dataclass
class SpeechAudio:
    data: bytes          # for example a WAV file
    mime_type: str       # "audio/wav"
    sample_rate: int
    provider: str | None = None


class SpeechToText(Protocol):
    def transcribe(self, audio: bytes, mime_type: str, language: str | None = None) -> Transcript: ...


class TextToSpeech(Protocol):
    def synthesize(self, text: str, language: str | None = None, voice: str | None = None) -> SpeechAudio: ...
