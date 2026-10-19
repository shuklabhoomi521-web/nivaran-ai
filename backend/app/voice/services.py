"""Pipecat services that wrap OUR speech interfaces (app/speech). Pipecat handles audio streaming, voice detection and
interruptions; the speech providers (Sarvam, Gemini, fakes in tests) stay swappable behind SpeechToText / TextToSpeech."""
import asyncio
import io
import time
import wave
from collections.abc import AsyncGenerator

from loguru import logger
from pipecat.frames.frames import ErrorFrame, Frame, TranscriptionFrame, TTSAudioRawFrame
from pipecat.services.settings import STTSettings, TTSSettings
from pipecat.services.stt_service import SegmentedSTTService
from pipecat.services.tts_service import TTSService
from pipecat.utils.time import time_now_iso8601

from app.speech.base import SpeechToText, TextToSpeech


class NivaranSTTService(SegmentedSTTService):
    """Hears one finished utterance (cut by the voice detector) and returns its text."""

    def __init__(self, stt: SpeechToText, language_hint: str | None = None, **kwargs):
        super().__init__(settings=STTSettings(model="nivaran", language=None), **kwargs)
        self._stt = stt
        self.language_hint = language_hint       # what the user picked: en-IN, hi-IN, ta-IN or hinglish
        self.last_seconds: float | None = None   # how long the last call took (for the delay panel)
        self.last_provider: str | None = None

    def can_generate_metrics(self) -> bool:
        return True

    async def run_stt(self, audio: bytes) -> AsyncGenerator[Frame, None]:
        t0 = time.time()
        try:
            # the provider call is blocking, so run it off the event loop (it must not freeze the audio)
            tr = await asyncio.to_thread(self._stt.transcribe, audio, "audio/wav", self.language_hint)
        except Exception as e:  # noqa: BLE001
            yield ErrorFrame(error=f"speech-to-text failed: {e}")
            return
        self.last_seconds = round(time.time() - t0, 2)
        self.last_provider = tr.provider
        logger.info(f"heard ({self.last_seconds}s, {tr.provider or 'primary'}): {tr.text!r}")
        if tr.text.strip():
            yield TranscriptionFrame(tr.text.strip(), self._user_id, time_now_iso8601())


class NivaranTTSService(TTSService):
    """Speaks one piece of text (one or two sentences) using our text-to-speech provider."""

    def __init__(self, tts: TextToSpeech, locale: str = "en-IN", **kwargs):
        super().__init__(pause_frame_processing=True, push_start_frame=True, push_stop_frames=True,
                         settings=TTSSettings(model="nivaran", voice=None, language=None), **kwargs)
        self._tts = tts
        self.locale = locale
        self.last_seconds: float | None = None
        self.last_provider: str | None = None

    def can_generate_metrics(self) -> bool:
        return True

    async def run_tts(self, text: str, context_id: str) -> AsyncGenerator[Frame, None]:
        t0 = time.time()
        try:
            audio = await asyncio.to_thread(self._tts.synthesize, text, self.locale)
            with wave.open(io.BytesIO(audio.data), "rb") as w:
                rate, channels, pcm = w.getframerate(), w.getnchannels(), w.readframes(w.getnframes())
        except Exception as e:  # noqa: BLE001
            yield ErrorFrame(error=f"text-to-speech failed: {e}")
            return
        self.last_seconds = round(time.time() - t0, 2)
        self.last_provider = audio.provider
        await self.stop_ttfb_metrics()
        logger.info(f"spoke {len(text)} chars in {self.last_seconds}s ({audio.provider or 'primary'})")
        yield TTSAudioRawFrame(pcm, rate, channels, context_id=context_id)
