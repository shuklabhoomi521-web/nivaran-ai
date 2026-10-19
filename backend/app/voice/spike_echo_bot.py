"""Spike: a bot that repeats what it heard. Proves the chain: browser microphone -> voice detector -> our speech-to-text ->
our text-to-speech -> browser speaker, with interruptions. The same `bot()` serves a phone provider in Phase 4 because
`create_transport` picks the transport (browser WebRTC, Twilio, Exotel, ...) from how the call arrives.

Run:  cd backend && python -m app.voice.spike_echo_bot      then open  http://localhost:7860/client
"""
import os

from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import (Frame, TranscriptionFrame, TTSSpeakFrame, VADUserStartedSpeakingFrame)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.audio.vad_processor import VADProcessor
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.transports.base_transport import TransportParams

from app.speech.factory import make_stt, make_tts
from app.voice.services import NivaranSTTService, NivaranTTSService

LOCALES = {"en-IN": "en-IN", "hi-IN": "hi-IN", "ta-IN": "ta-IN", "hinglish": "hi-IN"}   # hinglish is spoken back with the Hindi voice
SAY = {"en-IN": "You said: {t}", "hi-IN": "आपने कहा: {t}", "ta-IN": "நீங்கள் சொன்னது: {t}", "hinglish": "Aapne kaha: {t}"}


GREETING = {"en-IN": "Hello. Say something and I will repeat it.",
            "hi-IN": "नमस्ते। कुछ बोलिए, मैं दोहराऊँगा।",
            "ta-IN": "வணக்கம். ஏதாவது சொல்லுங்கள், நான் திரும்பச் சொல்கிறேன்.",
            "hinglish": "Namaste. Kuch boliye, main dohrata hoon."}


class Echo(FrameProcessor):
    """Turns what was heard into something to say back."""

    def __init__(self, language: str, **kwargs):
        super().__init__(**kwargs)
        self._language = language

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        if isinstance(frame, TranscriptionFrame):
            await self.push_frame(TTSSpeakFrame(SAY[self._language].format(t=frame.text)))
        else:
            await self.push_frame(frame, direction)


class InterruptOnSpeech(FrameProcessor):
    """If the user starts talking, stop whatever the bot is saying."""

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        if isinstance(frame, VADUserStartedSpeakingFrame):
            await self.broadcast_interruption()
        await self.push_frame(frame, direction)


def transport_params() -> dict:
    """One bot, many transports. Browser WebRTC today; Twilio / Exotel phone calls in Phase 4 use the same bot() and pipeline."""
    from pipecat.transports.websocket.fastapi import FastAPIWebsocketParams
    phone = lambda: FastAPIWebsocketParams(audio_in_enabled=True, audio_out_enabled=True)  # noqa: E731
    return {"webrtc": lambda: TransportParams(audio_in_enabled=True, audio_out_enabled=True), "twilio": phone, "exotel": phone}


async def bot(runner_args: RunnerArguments):
    language = os.getenv("VOICE_LANGUAGE", "en-IN")
    transport = await create_transport(runner_args, transport_params())
    stt = NivaranSTTService(make_stt(), language_hint=language)
    tts = NivaranTTSService(make_tts(), locale=LOCALES[language])
    pipeline = Pipeline([
        transport.input(),
        VADProcessor(vad_analyzer=SileroVADAnalyzer()),
        InterruptOnSpeech(),
        stt,
        Echo(language),
        tts,
        transport.output(),
    ])
    task = PipelineTask(pipeline, params=PipelineParams(enable_metrics=True))

    @transport.event_handler("on_client_connected")
    async def _connected(_t, _c):
        logger.info(f"client connected; language {language}")
        await task.queue_frames([TTSSpeakFrame(GREETING[language])])

    @transport.event_handler("on_client_disconnected")
    async def _disconnected(_t, _c):
        logger.info("client disconnected")
        try:
            from app.speech.credits import CreditLedger
            logger.info(CreditLedger().session_line())      # credits used in this test session
        except Exception:  # noqa: BLE001
            pass
        await task.cancel()

    await PipelineRunner(handle_sigint=False).run(task)


if __name__ == "__main__":
    from pipecat.runner.run import main
    main()
