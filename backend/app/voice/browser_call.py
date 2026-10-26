"""PHONE CALL PRACTICE IN THE BROWSER (the fallback when a real phone call is not possible).
The person in the browser plays the customer-care agent. The AI is exactly the one that would phone a company: same disclosure, same brain,
keypad presses, hold-music detection, transcript. The only difference is the line: here the sound is squeezed to phone quality (8 kHz mu-law)
on both sides, so the speech-to-text hears what it would hear on a real call. Not tested this way: real phone carriers, real call set-up."""
import asyncio
import uuid

from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import TTSSpeakFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.audio.vad_processor import VADProcessor
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport

from app.voice import transcripts
from app.voice.call_conversation import CallConversation
from app.voice.events import log_event
from app.voice.hold import HoldProcessor
from app.voice.phone_bot import ACTIVE, DEFAULT_CASE, CallProcessor
from app.voice.phone_quality import PhoneLine
from app.voice.services import NivaranSTTService, NivaranTTSService
from app.voice.spike_echo_bot import InterruptOnSpeech, transport_params


async def browser_call_bot(runner_args: RunnerArguments, llm=None, stt_provider=None, tts_provider=None):
    body = getattr(runner_args, "body", None) or {}
    language = body.get("language") if body.get("language") in ("en-IN", "hi-IN", "ta-IN", "hinglish") else "en-IN"
    case = body.get("case") or DEFAULT_CASE
    if llm is None or stt_provider is None or tts_provider is None:
        from app.brain.llm import make_llm
        from app.speech.factory import make_stt, make_tts
        llm, stt_provider, tts_provider = await asyncio.gather(asyncio.to_thread(make_llm), asyncio.to_thread(make_stt), asyncio.to_thread(make_tts))
    call = CallConversation(case, language, llm)
    transport = await create_transport(runner_args, transport_params())
    stt = NivaranSTTService(stt_provider, language_hint="auto", trailing_silence_secs=0.3)
    tts = NivaranTTSService(tts_provider, locale=language)
    transcript: list[dict] = []
    hold = HoldProcessor(on_change=lambda on: proc.note("system", "on hold: waiting quietly" if on else "off hold: someone is talking again"))
    proc = CallProcessor(call, stt, tts, transcript, hold)
    pipeline = Pipeline([
        transport.input(), PhoneLine(),                                   # what the agent says, squeezed like a phone line
        VADProcessor(vad_analyzer=SileroVADAnalyzer(params=VADParams(confidence=0.6, min_volume=0.1, start_secs=0.2, stop_secs=0.7))),
        hold, InterruptOnSpeech(), stt, proc, tts,
        PhoneLine(), transport.output(),                                  # what the AI says, squeezed too
    ])
    task = PipelineTask(pipeline, params=PipelineParams(enable_metrics=True))
    call_id = "browser-" + uuid.uuid4().hex[:8]
    ACTIVE[call_id] = proc
    proc.stop = lambda: task.cancel()

    @transport.event_handler("on_client_connected")
    async def _connected(_t, _c):
        log_event("info", f"practice phone call connected (browser, phone-quality sound) ({language})")
        opening = call.opening()                                          # fixed text: "I am an AI assistant calling on behalf of a customer ..."
        proc.note("ai", opening)
        await task.queue_frames([TTSSpeakFrame(opening)])

    @transport.event_handler("on_client_disconnected")
    async def _disconnected(_t, _c):
        proc.note("system", "line closed")
        await task.cancel()

    try:
        await PipelineRunner(handle_sigint=False).run(task)
    finally:
        ACTIVE.pop(call_id, None)
        if transcript:
            try:
                transcripts.save(call_id, transcript)
            except Exception:  # noqa: BLE001
                logger.exception("could not save the transcript")
        try:
            from app.speech.credits import CreditLedger
            log_event("info", CreditLedger().session_line())
        except Exception:  # noqa: BLE001
            pass
