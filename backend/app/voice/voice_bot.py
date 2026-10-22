"""The real voice bot: you speak your problem, it asks one question at a time, then says what it understood.
Same transports as the echo spike (browser now, phone in Phase 4)."""
import asyncio
import os
import time

from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import (CancelFrame, EndFrame, Frame, TranscriptionFrame, TTSSpeakFrame,
                                   UserStartedSpeakingFrame, UserStoppedSpeakingFrame)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.audio.vad_processor import VADProcessor
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport

from app.brain.llm import make_llm
from app.safety.redact import redact
from app.speech.factory import make_stt, make_tts
from app.voice.conversation import FILLER, Conversation
from app.voice.events import log_event
from app.voice.services import NivaranSTTService, NivaranTTSService
from app.voice.spike_echo_bot import InterruptOnSpeech, MicLevelLogger, transport_params

LANGUAGES = ("en-IN", "hi-IN", "ta-IN", "hinglish")


class ConversationProcessor(FrameProcessor):
    """What was heard -> what to say.

    The brain can take seconds (the free AI service is sometimes slow), so it runs in its own background task:
    - talking over the bot never cancels a half-finished answer (an interruption used to throw the reply away);
    - if you say something else while we are still thinking, your sentences are joined and answered together;
    - if thinking takes long, we say "one moment" so you are not left in silence."""

    SLOW_AFTER = 6.0     # seconds of thinking before we say "one moment"

    def __init__(self, conversation: Conversation, stt: NivaranSTTService, **kwargs):
        super().__init__(**kwargs)
        self._conv, self._stt = conversation, stt
        self._pending: list[str] = []
        self._worker: asyncio.Task | None = None
        self._user_talking = False
        self._filler_done = False      # "one moment" is said at most once per answer

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        if isinstance(frame, (CancelFrame, EndFrame)) and self._worker and not self._worker.done():
            self._worker.cancel()
        if isinstance(frame, UserStartedSpeakingFrame):
            self._user_talking = True
        elif isinstance(frame, UserStoppedSpeakingFrame):
            self._user_talking = False
        if not isinstance(frame, TranscriptionFrame):
            await self.push_frame(frame, direction)
            return
        log_event("heard", redact(frame.text, strict=True)[0], secs=self._stt.last_seconds)   # the page log never shows card numbers
        self._pending.append(frame.text)
        if self._worker is None or self._worker.done():
            self._worker = asyncio.create_task(self._think())

    async def _think(self):
        while self._pending:
            said = " ".join(self._pending)
            self._pending.clear()
            snap = self._conv.snapshot()
            log_event("thinking", "…")
            t0 = time.time()
            filler = None if self._filler_done else asyncio.create_task(self._say_filler_if_slow())
            try:
                turn = await asyncio.to_thread(self._conv.handle, said)
            except Exception as e:  # noqa: BLE001 - a brain failure must not kill the call
                logger.exception("brain failed")
                log_event("err", f"The assistant had a problem thinking: {e}")
                self._conv.restore(snap)
                continue
            finally:
                if filler:
                    filler.cancel()
            if self._pending:                       # you kept talking: forget this answer and answer everything together
                self._conv.restore(snap)
                self._pending.insert(0, said)
                continue
            log_event("note", turn.note, secs=round(time.time() - t0, 1))
            log_event("spoke", turn.reply)
            self._filler_done = False               # next answer may use "one moment" again
            await self.push_frame(TTSSpeakFrame(turn.reply))

    async def _say_filler_if_slow(self):
        try:
            await asyncio.sleep(self.SLOW_AFTER)
            while self._user_talking or self._pending:      # never talk over the user, never while a newer sentence waits
                await asyncio.sleep(0.3)
            self._filler_done = True
            await self.push_frame(TTSSpeakFrame(FILLER.get(self._conv.language, FILLER["en-IN"])))
        except asyncio.CancelledError:
            pass


async def bot(runner_args: RunnerArguments):
    body = getattr(runner_args, "body", None) or {}
    language = body.get("language") or os.getenv("VOICE_LANGUAGE", "en-IN")
    language = language if language in LANGUAGES else "en-IN"
    # building the providers can import big libraries: never do that on the audio thread
    llm, stt_provider, tts_provider = await asyncio.gather(asyncio.to_thread(make_llm), asyncio.to_thread(make_stt), asyncio.to_thread(make_tts))
    conv = Conversation(language, llm)
    transport = await create_transport(runner_args, transport_params())
    stt = NivaranSTTService(stt_provider, language_hint=language, trailing_silence_secs=0.3)
    tts = NivaranTTSService(tts_provider, locale=language)
    pipeline = Pipeline([
        transport.input(),
        MicLevelLogger(),
        VADProcessor(vad_analyzer=SileroVADAnalyzer(params=VADParams(confidence=0.5, min_volume=0.1, start_secs=0.2, stop_secs=0.5))),
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
