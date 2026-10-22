"""The real voice bot: you speak your problem, it asks one question at a time, then says what it understood.
Same transports as the echo spike (browser now, phone in Phase 4)."""
import asyncio
import os
import time

from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import Frame, TranscriptionFrame, TTSSpeakFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.audio.vad_processor import VADProcessor
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport

from app.brain.llm import make_llm
from app.speech.factory import make_stt, make_tts
from app.voice.conversation import Conversation
from app.voice.events import log_event
from app.voice.services import NivaranSTTService, NivaranTTSService
from app.voice.spike_echo_bot import InterruptOnSpeech, MicLevelLogger, transport_params

LANGUAGES = ("en-IN", "hi-IN", "ta-IN", "hinglish")


class ConversationProcessor(FrameProcessor):
    """What was heard -> what to say. The brain calls block, so they run off the audio thread."""

    def __init__(self, conversation: Conversation, stt: NivaranSTTService, **kwargs):
        super().__init__(**kwargs)
        self._conv, self._stt = conversation, stt

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        if not isinstance(frame, TranscriptionFrame):
            await self.push_frame(frame, direction)
            return
        log_event("heard", frame.text, secs=self._stt.last_seconds)
        t0 = time.time()
        try:
            turn = await asyncio.to_thread(self._conv.handle, frame.text)
        except Exception as e:  # noqa: BLE001 - a brain failure must not kill the call
            logger.exception("brain failed")
            log_event("err", f"The assistant had a problem thinking: {e}")
            return
        log_event("note", turn.note, secs=round(time.time() - t0, 1))
        log_event("spoke", turn.reply)
        await self.push_frame(TTSSpeakFrame(turn.reply))


async def bot(runner_args: RunnerArguments):
    body = getattr(runner_args, "body", None) or {}
    language = body.get("language") or os.getenv("VOICE_LANGUAGE", "en-IN")
    language = language if language in LANGUAGES else "en-IN"
    conv = Conversation(language, make_llm())
    transport = await create_transport(runner_args, transport_params())
    stt = NivaranSTTService(make_stt(), language_hint=language)
    tts = NivaranTTSService(make_tts(), locale=language)
    pipeline = Pipeline([
        transport.input(),
        MicLevelLogger(),
        VADProcessor(vad_analyzer=SileroVADAnalyzer(params=VADParams(confidence=0.5, min_volume=0.1, start_secs=0.2, stop_secs=0.7))),
        InterruptOnSpeech(),
        stt,
        ConversationProcessor(conv, stt),
        tts,
        transport.output(),
    ])
    task = PipelineTask(pipeline, params=PipelineParams(enable_metrics=True))

    @transport.event_handler("on_client_connected")
    async def _connected(_t, _c):
        log_event("info", f"connected ({language})")
        log_event("spoke", conv.greeting())
        await task.queue_frames([TTSSpeakFrame(conv.greeting())])

    @transport.event_handler("on_client_disconnected")
    async def _disconnected(_t, _c):
        try:
            from app.speech.credits import CreditLedger
            line = CreditLedger().session_line()
            logger.info(line)
            log_event("info", line)
        except Exception:  # noqa: BLE001
            pass
        await task.cancel()

    await PipelineRunner(handle_sigint=False).run(task)
