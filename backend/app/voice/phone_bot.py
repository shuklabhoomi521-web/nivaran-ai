"""The voice bot on a PHONE CALL (Twilio Media Streams, 8 kHz). The other side is a customer-care agent (in Phase 4: the founder's friend).
Same ears and mouth as the browser bot; the brain is CallConversation (speaks FOR the user, starts with the AI disclosure)."""
import asyncio
import os
import time

from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import (CancelFrame, EndFrame, Frame, OutputAudioRawFrame, TranscriptionFrame, TTSSpeakFrame,
                                   UserStartedSpeakingFrame, UserStoppedSpeakingFrame)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.audio.vad_processor import VADProcessor
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.runner.utils import parse_telephony_websocket
from pipecat.serializers.twilio import TwilioFrameSerializer
from pipecat.transports.websocket.fastapi import FastAPIWebsocketParams, FastAPIWebsocketTransport

from app.safety.redact import redact, scrub
from app.voice import transcripts
from app.voice.call_conversation import _SECRET_ASK, CallConversation
from app.voice.conversation import FILLER
from app.voice.dtmf import tones
from app.voice.events import log_event
from app.voice.hold import HoldProcessor
from app.voice.services import NivaranSTTService, NivaranTTSService
from app.voice.spike_echo_bot import InterruptOnSpeech

DEFAULT_CASE = {"company": "Swiggy", "problem_summary": "The order arrived cold and no refund was given.", "user_goal": "refund",
                "details_known": [{"name": "order_id", "value": "4839201"}]}      # the practice case (made-up facts)
PENDING_CALLS: dict[str, dict] = {}       # case_id -> {"case": ..., "language": ...}; set by the "start a call" endpoint, read when Twilio connects
ACTIVE: dict[str, "CallProcessor"] = {}   # call id -> running call (so the user's Stop button can end it)


class CallProcessor(FrameProcessor):
    """What the agent said -> what we say (or which keypad button we press). Thinking runs in the background so the audio never freezes."""

    BRAIN_DEADLINE = 15.0
    SLOW_AFTER = 5.0

    def __init__(self, call: CallConversation, stt: NivaranSTTService, tts: NivaranTTSService, transcript: list, hold: HoldProcessor | None = None, **kwargs):
        super().__init__(**kwargs)
        self.call, self._stt, self._tts, self.transcript, self._hold = call, stt, tts, transcript, hold
        self._t0 = time.time()
        self._pending: list[str] = []
        self._worker: asyncio.Task | None = None
        self._agent_talking = False
        self._filler_done = False

    # ---- the user's controls during a call (the "Join call" panel) ----
    muted = False

    def set_muted(self, on: bool) -> None:
        """Mute the AI: it keeps listening and writing the transcript but says nothing, so the user can take over."""
        self.muted = on
        self.note("system", "AI muted: the user is in control" if on else "AI unmuted")
        if on and self._worker and not self._worker.done():
            self._worker.cancel()

    async def say_for_user(self, text: str) -> str:
        """The user typed something; the AI voices it exactly. Secrets are refused (never spoken on a call)."""
        clean = scrub({"t": text})[0]["t"].strip()
        if not clean:
            raise ValueError("Nothing to say.")
        if _SECRET_ASK.search(clean) or clean != text.strip():
            raise ValueError("That looks like a card number, PIN, password or one-time code. Those are never spoken on a call.")
        await self._speak(clean, who="user")
        return clean

    def note(self, who: str, text: str) -> None:
        self.transcript.append({"who": who, "text": text, "t": round(time.time() - self._t0, 1)})
        log_event({"agent": "heard", "ai": "spoke", "user": "spoke"}.get(who, "info"), ("(you) " if who == "user" else "") + redact(text, strict=True)[0])

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        if isinstance(frame, (CancelFrame, EndFrame)) and self._worker and not self._worker.done():
            self._worker.cancel()
        if isinstance(frame, UserStartedSpeakingFrame):
            self._agent_talking = True
        elif isinstance(frame, UserStoppedSpeakingFrame):
            self._agent_talking = False
        if not isinstance(frame, TranscriptionFrame):
            await self.push_frame(frame, direction)
            return
        self.note("agent", frame.text)
        if self.muted:
            return                                    # the user has taken over: do not answer
        if self._hold is not None and self._hold.on_hold and len(frame.text.split()) < 4:
            return                                    # music or a few stray words while on hold: keep waiting quietly
        self._pending.append(frame.text)
        if self._worker is None or self._worker.done():
            self._worker = asyncio.create_task(self._think())

    async def _think(self):
        while self._pending and not self.call.ended:
            said = " ".join(self._pending)
            self._pending.clear()
            filler = None if self._filler_done else asyncio.create_task(self._say_filler_if_slow())
            n_before = len(self.call.history)
            loop, futures, live = asyncio.get_running_loop(), [], {"on": True}

            def on_sentence(sentence: str, futures=futures, live=live, loop=loop):
                """Called from the brain's thread for each finished sentence: speak it NOW (unless the agent is talking or we gave up)."""
                if live["on"] and not (self._agent_talking or self._pending):
                    futures.append(asyncio.run_coroutine_threadsafe(self._speak(sentence), loop))

            try:
                reply = await asyncio.wait_for(asyncio.to_thread(self.call.respond, said, on_sentence), self.BRAIN_DEADLINE)
            except Exception as e:  # noqa: BLE001 - never go silent, never crash the call
                live["on"] = False
                logger.exception("call brain failed")
                log_event("err", f"call brain problem: {type(e).__name__}")
                del self.call.history[n_before:]
                if not self._pending:
                    await self._speak("Sorry, could you please repeat that?")
                continue
            finally:
                live["on"] = False
                if filler:
                    filler.cancel()
            await asyncio.gather(*[asyncio.wrap_future(f) for f in futures])      # let the streamed sentences finish being queued, in order
            if self._pending:                         # the agent kept talking: answer everything together
                del self.call.history[n_before - 1:]
                self._pending.insert(0, said)
                continue
            self._filler_done = False
            action = self.call.last_action
            if action == "press_digits":
                self.note("system", f"pressed keypad: {self.call.last_digits}")
                await self.push_frame(OutputAudioRawFrame(audio=tones(self.call.last_digits), sample_rate=8000, num_channels=1))
            else:
                if not self.call.streamed:                # (streamed answers were already spoken sentence by sentence)
                    await self._speak(reply)
                if action == "need_user":
                    self.note("system", "the agent asked for something we do not have: the user is needed")
            if self.call.ended:
                self.note("system", "call ended by the AI")
                await self.push_frame(EndFrame())
                return

    async def _speak(self, text: str, who: str = "ai"):
        self.note(who, text)
        await self.push_frame(TTSSpeakFrame(text))

    async def _say_filler_if_slow(self):
        try:
            await asyncio.sleep(self.SLOW_AFTER)
            while self._agent_talking or self._pending:
                await asyncio.sleep(0.3)
            self._filler_done = True
            await self.push_frame(TTSSpeakFrame(FILLER.get(self.call.language, FILLER["en-IN"])))
        except asyncio.CancelledError:
            pass


async def run_call_bot(websocket, llm=None, stt_provider=None, tts_provider=None, case: dict | None = None, language: str | None = None,
                       auto_hang_up: bool = True, save_transcript: bool = True, transcript: list | None = None, require_pending: bool = False) -> list[dict]:
    """Serve one phone call on an open Twilio websocket. Returns the transcript. Providers can be passed in (tests use fakes)."""
    transport_type, call_data = await parse_telephony_websocket(websocket)
    if transport_type != "twilio":
        raise ValueError(f"Phase 4 supports Twilio only, got {transport_type}")
    pending = PENDING_CALLS.pop((call_data.body or {}).get("case_id", ""), None)
    if require_pending and pending is None:             # nobody asked for this call (a stranger found the websocket): hang up, spend nothing
        await websocket.close()
        return []
    pending = pending or {}
    case = case or pending.get("case") or {}
    language = language or pending.get("language") or "en-IN"
    if llm is None or stt_provider is None or tts_provider is None:
        from app.brain.llm import make_llm
        from app.speech.factory import make_stt, make_tts
        llm, stt_provider, tts_provider = await asyncio.gather(asyncio.to_thread(make_llm), asyncio.to_thread(make_stt), asyncio.to_thread(make_tts))
    call = CallConversation(case, language, llm)
    serializer = TwilioFrameSerializer(
        stream_sid=call_data["stream_id"], call_sid=call_data["call_id"], account_sid=os.getenv("TWILIO_ACCOUNT_SID", ""),
        auth_token=os.getenv("TWILIO_AUTH_TOKEN", ""), params=TwilioFrameSerializer.InputParams(auto_hang_up=auto_hang_up))
    transport = FastAPIWebsocketTransport(websocket=websocket, params=FastAPIWebsocketParams(
        audio_in_enabled=True, audio_out_enabled=True, add_wav_header=False, serializer=serializer,
        audio_in_sample_rate=8000, audio_out_sample_rate=8000))
    stt = NivaranSTTService(stt_provider, language_hint="auto", trailing_silence_secs=0.3)
    tts = NivaranTTSService(tts_provider, locale=language)
    transcript = [] if transcript is None else transcript          # the caller may pass its own list and read it while the call runs
    hold = HoldProcessor(on_change=lambda on: proc.note("system", "on hold: waiting quietly" if on else "off hold: someone is talking again"))
    proc = CallProcessor(call, stt, tts, transcript, hold)
    pipeline = Pipeline([
        transport.input(),
        VADProcessor(vad_analyzer=SileroVADAnalyzer(params=VADParams(confidence=0.6, min_volume=0.1, start_secs=0.2, stop_secs=0.7))),
        hold, InterruptOnSpeech(), stt, proc, tts, transport.output(),
    ])
    task = PipelineTask(pipeline, params=PipelineParams(enable_metrics=True, audio_in_sample_rate=8000, audio_out_sample_rate=8000))
    call_id = call_data["call_id"]
    ACTIVE[call_id] = proc

    @transport.event_handler("on_client_connected")
    async def _connected(_t, _c):
        log_event("info", f"phone call connected ({language})")
        opening = call.opening()                         # fixed text: "I am an AI assistant calling on behalf of a customer ..."
        proc.note("ai", opening)
        await task.queue_frames([TTSSpeakFrame(opening)])

    @transport.event_handler("on_client_disconnected")
    async def _disconnected(_t, _c):
        proc.note("system", "line closed")
        await task.cancel()

    proc.stop = lambda: task.cancel()                    # the user's Stop button
    try:
        await PipelineRunner(handle_sigint=False).run(task)
    finally:
        ACTIVE.pop(call_id, None)
        if save_transcript and transcript:
            try:
                transcripts.save(call_id, transcript)
            except Exception:  # noqa: BLE001
                logger.exception("could not save the transcript")
        try:
            from app.speech.credits import CreditLedger
            log_event("info", CreditLedger().session_line())
        except Exception:  # noqa: BLE001
            pass
    return transcript
