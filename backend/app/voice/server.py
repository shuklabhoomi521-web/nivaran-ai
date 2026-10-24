"""Our own small server for the voice page (instead of Pipecat's generic playground): one page, one WebRTC endpoint, a log of
what the bot heard and said. Later this is mounted into the main FastAPI app.

Run:  cd backend && python -m app.voice.server      then open  http://localhost:7861/voice
"""
import os
import uuid
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI
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

    async def callback(connection: SmallWebRTCConnection):
        args = SmallWebRTCRunnerArguments(webrtc_connection=connection, body=request.request_data, session_id=str(uuid.uuid4()))
        background_tasks.add_task(bot, args)

    return await handler.handle_web_request(request=request, webrtc_connection_callback=callback)


@app.patch("/voice/api/offer")
async def ice(request: SmallWebRTCPatchRequest):
    await handler.handle_patch_request(request)
    return {"status": "success"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=int(os.getenv("VOICE_PORT", "7861")))
