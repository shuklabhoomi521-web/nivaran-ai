"""Our own small server for the voice page (instead of Pipecat's generic playground): one page, one WebRTC endpoint, a log of
what the bot heard and said. Later this is mounted into the main FastAPI app.

Run:  cd backend && python -m app.voice.server      then open  http://localhost:7861/voice
"""
import os
import uuid
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException, WebSocket
from fastapi.responses import FileResponse
from pipecat.runner.types import SmallWebRTCRunnerArguments

from app.voice.events import EVENTS
from pipecat.transports.smallwebrtc.connection import SmallWebRTCConnection
from pipecat.transports.smallwebrtc.request_handler import (SmallWebRTCPatchRequest, SmallWebRTCRequest,
                                                            SmallWebRTCRequestHandler)

STATIC = Path(__file__).resolve().parents[2] / "static"
app = FastAPI(title="Nivaran voice test")
handler = SmallWebRTCRequestHandler()

READY = {"ok": False}


def _warm_up() -> None:
    """Load every heavy library and model once, BEFORE the first call. Loading them in the middle of a call froze the audio for a few
    seconds and broke that first session (the connection timed out while the server was busy importing)."""
    from pipecat.audio.vad.silero import SileroVADAnalyzer

    from app.brain.llm import make_llm
    from app.speech.factory import make_stt, make_tts
    import app.voice.voice_bot  # noqa: F401
    make_llm(); stt = make_stt(); make_tts()
    for part in (stt, getattr(stt, 'primary', None)):      # the free local model takes ~20 s to load: do it now, not on the first sentence
        if hasattr(part, '_pipe'):
            part._pipe()
    SileroVADAnalyzer()
    READY["ok"] = True


@app.on_event("startup")
async def warm_up():
    import asyncio
    asyncio.get_event_loop().run_in_executor(None, _warm_up)


@app.get("/voice/ready")
async def ready():
    return {"ready": READY["ok"]}


@app.get("/voice/choice/{name:path}")
async def voice_choice(name: str):
    """The voice-choice listening page and its audio files (synthetic voices only)."""
    base = STATIC.parent.parent / "speech_test" / "voice_choice"
    target = (base / (name or "index.html")).resolve()
    if base.resolve() not in target.parents and target != base.resolve():
        return FileResponse(base / "index.html")
    return FileResponse(target if target.is_file() else base / "index.html")


@app.get("/voice")
async def voice_page():
    return FileResponse(STATIC / "voice_test.html")


@app.get("/voice/events")
async def events(since: int = 0):
    return [e for e in EVENTS if e["n"] > since]


@app.post("/voice/api/offer")
async def offer(request: SmallWebRTCRequest, background_tasks: BackgroundTasks):
    from app.voice.voice_bot import bot   # the real bot; the echo spike stays in spike_echo_bot.py for diagnostics
    if (request.request_data or {}).get("mode") == "phone":      # the phone-call practice in the browser (the AI phones, you play the agent)
        from app.voice.browser_call import browser_call_bot as bot  # noqa: F811

    async def callback(connection: SmallWebRTCConnection):
        args = SmallWebRTCRunnerArguments(webrtc_connection=connection, body=request.request_data, session_id=str(uuid.uuid4()))
        background_tasks.add_task(bot, args)

    return await handler.handle_web_request(request=request, webrtc_connection_callback=callback)


@app.patch("/voice/api/offer")
async def ice(request: SmallWebRTCPatchRequest):
    await handler.handle_patch_request(request)
    return {"status": "success"}


# ---- phone calls (Phase 4) -------------------------------------------------------------------------------------------------------------
from pydantic import BaseModel  # noqa: E402


class CallRequest(BaseModel):
    to_number: str
    case: dict                       # company, problem_summary, user_goal, details_known
    language: str = "en-IN"
    confirm: bool = False            # the user must say yes to THIS call
    say_only: bool = False           # line test: the phone just speaks a short sentence (no AI, no audio stream) to prove the call itself works


REHEARSAL_CASE = {"company": "Swiggy", "problem_summary": "The order arrived cold and no refund was given.", "user_goal": "refund",
                  "details_known": [{"name": "order_id", "value": "4839201"}]}


@app.post("/phone/call")
async def start_call(req: CallRequest):
    """Start an outbound call. Needs confirm=true (the user's OK for this exact call) and a number on the allow-list."""
    from app.channels.phone.twilio import PhoneError, TwilioPhone
    from app.voice.phone_bot import PENDING_CALLS
    if not req.confirm:
        raise HTTPException(400, "The user has not confirmed this call.")
    base = os.getenv("PUBLIC_BASE_URL", "").strip().rstrip("/")
    if not base.startswith("https://"):
        raise HTTPException(400, "PUBLIC_BASE_URL (the public https address of this server) is not set.")
    case_id = uuid.uuid4().hex
    PENDING_CALLS[case_id] = {"case": req.case, "language": req.language, "say_only": req.say_only}
    try:
        call_id = await TwilioPhone().place_call(req.to_number, f"{base}/phone/twiml?case_id={case_id}")
    except PhoneError as e:
        PENDING_CALLS.pop(case_id, None)
        raise HTTPException(400, str(e))
    return {"call_id": call_id}


@app.api_route("/phone/twiml", methods=["GET", "POST"])
async def twiml(case_id: str = ""):
    """Twilio asks this when the phone is answered: 'what do I do with this call?' Answer: stream the audio to our bot's websocket."""
    from fastapi.responses import Response

    from app.channels.phone.twilio import stream_twiml
    from app.voice.phone_bot import PENDING_CALLS
    base = os.getenv("PUBLIC_BASE_URL", "").strip().rstrip("/")
    if case_id not in PENDING_CALLS or not base.startswith("https://"):
        return Response("<Response><Say>Sorry, this call is not set up.</Say><Hangup/></Response>", media_type="text/xml")
    if PENDING_CALLS[case_id].get("say_only"):         # line test: no AI, no audio stream
        PENDING_CALLS.pop(case_id, None)
        return Response("<Response><Say>Hello. This is the Nivaran line test. The call works. Goodbye.</Say><Hangup/></Response>", media_type="text/xml")
    return Response(stream_twiml(base.replace("https://", "wss://") + "/phone/ws", {"case_id": case_id}), media_type="text/xml")


@app.post("/phone/hangup/{call_id}")
async def hang_up(call_id: str):
    """The user's Stop button: ends the call right now."""
    from app.voice.phone_bot import ACTIVE
    proc = ACTIVE.get(call_id)
    if proc is None:
        raise HTTPException(404, "No such active call.")
    await proc.stop()
    return {"ended": True}


@app.websocket("/phone/ws")
async def phone_ws(websocket: WebSocket):
    from app.voice.phone_bot import run_call_bot
    await websocket.accept()
    if os.getenv("PHONE_REHEARSAL"):             # practice mode: a pretend company on a pretend phone (scripts/fake_company_call.py), no real call
        await run_call_bot(websocket, case=REHEARSAL_CASE, language="en-IN", auto_hang_up=False)
    else:
        await run_call_bot(websocket, require_pending=True)


class SayRequest(BaseModel):
    text: str


@app.get("/phone/calls")
async def active_calls():
    from app.voice.phone_bot import ACTIVE
    return [{"call_id": cid, "muted": p.muted, "company": p.call.company, "on_hold": bool(p._hold and p._hold.on_hold)} for cid, p in ACTIVE.items()]


@app.post("/phone/mute/{call_id}")
async def mute(call_id: str, on: bool = True):
    from app.voice.phone_bot import ACTIVE
    proc = ACTIVE.get(call_id)
    if proc is None:
        raise HTTPException(404, "No such active call.")
    proc.set_muted(on)
    return {"muted": proc.muted}


@app.post("/phone/say/{call_id}")
async def say(call_id: str, req: SayRequest):
    """Join the call in writing: the AI says what the user typed (and only that)."""
    from app.voice.phone_bot import ACTIVE
    proc = ACTIVE.get(call_id)
    if proc is None:
        raise HTTPException(404, "No such active call.")
    try:
        return {"said": await proc.say_for_user(req.text)}
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.get("/phone/browser")
async def browser_call_page():
    return FileResponse(STATIC / "phone_browser.html")


@app.get("/phone/control")
async def control_page():
    return FileResponse(STATIC / "call_control.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=int(os.getenv("VOICE_PORT", "7861")))
