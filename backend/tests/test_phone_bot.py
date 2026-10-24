"""A pretend Twilio call: the test plays Twilio (sends the same websocket messages, with 8 kHz mu-law phone audio) and the real phone bot answers.
No network, no phone, no account. Fake speech providers and a scripted AI."""
import audioop
import base64
import json
import signal
import wave
from pathlib import Path

import numpy as np
import pytest
from fastapi import FastAPI, WebSocket
from starlette.testclient import TestClient

from app.speech.fakes import FakeSTT
from app.voice.call_conversation import DISCLOSURE
from app.voice.phone_bot import run_call_bot
from tests.test_call_conversation import CASE, Scripted, turn
from tests.test_voice_services import WavTTS

CLIP = Path(__file__).resolve().parents[2] / "speech_test" / "live_clips" / "answer_order_number.wav"


def mulaw_chunks(path: Path, silence_secs: float = 2.5):
    with wave.open(str(path), "rb") as w:
        rate, pcm = w.getframerate(), np.frombuffer(w.readframes(w.getnframes()), "<i2")
    x = np.interp(np.arange(0, len(pcm), rate / 8000), np.arange(len(pcm)), pcm).astype("<i2")      # down to 8 kHz like a phone line
    x = np.concatenate([x, np.zeros(int(8000 * silence_secs), "<i2")])
    ulaw = audioop.lin2ulaw(x.tobytes(), 2)
    return [ulaw[i:i + 160] for i in range(0, len(ulaw), 160)]                                       # 20 ms pieces


def twilio_start(case_id="x"):
    return [json.dumps({"event": "connected", "protocol": "Call", "version": "1.0.0"}),
            json.dumps({"event": "start", "sequenceNumber": "1", "streamSid": "MZtest",
                        "start": {"accountSid": "ACtest", "streamSid": "MZtest", "callSid": "CAtest", "tracks": ["inbound"],
                                  "mediaFormat": {"encoding": "audio/x-mulaw", "sampleRate": 8000, "channels": 1},
                                  "customParameters": {"case_id": case_id}}})]


def build_app(llm, stt, tts, out):
    app = FastAPI()

    @app.websocket("/phone/ws")
    async def ws(websocket: WebSocket):
        await websocket.accept()
        out["transcript"] = []
        await run_call_bot(websocket, llm=llm, stt_provider=stt, tts_provider=tts, case=CASE, language="en-IN",
                           auto_hang_up=False, save_transcript=False, transcript=out["transcript"])
    return app


@pytest.mark.skipif(not CLIP.exists(), reason="needs local test clips (kept out of git)")
def test_the_ai_introduces_itself_first_then_answers_the_agent():
    signal.alarm(120)
    try:
        llm, tts, out = Scripted(turn("My customer's order ID is 4839201 and they want a refund.")), WavTTS(), {}
        client = TestClient(build_app(llm, FakeSTT("How can I help you?"), tts, out))
        with client.websocket_connect("/phone/ws") as ws:
            for m in twilio_start():
                ws.send_text(m)
            got = []
            # 1) the bot speaks first: the fixed AI disclosure
            while "media" not in [json.loads(g).get("event") for g in got]:
                got.append(ws.receive_text())
            assert tts.calls[0][0] == DISCLOSURE["en-IN"].format(company="Swiggy") and "AI assistant" in tts.calls[0][0]
            # 2) the agent speaks (the test plays a clip), the bot answers
            for chunk in mulaw_chunks(CLIP):
                ws.send_text(json.dumps({"event": "media", "streamSid": "MZtest", "media": {"track": "inbound", "payload": base64.b64encode(chunk).decode()}}))
            while len(tts.calls) < 2:
                got.append(ws.receive_text())
            ws.send_text(json.dumps({"event": "stop", "streamSid": "MZtest"}))
        assert tts.calls[1][0].startswith("My customer's order ID is 4839201")
        who = [t["who"] for t in out.get("transcript", [])]
        assert [w for w in who if w != "system"][:3] == ["ai", "agent", "ai"], who
        media = [json.loads(g) for g in got if json.loads(g).get("event") == "media"]
        assert media and all(m["streamSid"] == "MZtest" for m in media)       # audio goes back out on the same call
    finally:
        signal.alarm(0)


def _run_one_agent_turn(llm, agent_says):
    tts, out = WavTTS(), {}
    client = TestClient(build_app(llm, FakeSTT(agent_says), tts, out))
    got = []
    with client.websocket_connect("/phone/ws") as ws:
        for m in twilio_start():
            ws.send_text(m)
        while len(got) < 1 or "media" not in [json.loads(g).get("event") for g in got]:
            got.append(ws.receive_text())
        n_before = len(got)
        for chunk in mulaw_chunks(CLIP):
            ws.send_text(json.dumps({"event": "media", "streamSid": "MZtest", "media": {"track": "inbound", "payload": base64.b64encode(chunk).decode()}}))
        import time
        t0 = time.time()
        while time.time() - t0 < 20 and not any("pressed keypad" in t["text"] or "ended by the AI" in t["text"] for t in out["transcript"]):
            time.sleep(0.2)
        ws.send_text(json.dumps({"event": "stop", "streamSid": "MZtest"}))
    return tts, out["transcript"]


@pytest.mark.skipif(not CLIP.exists(), reason="needs local test clips (kept out of git)")
def test_a_phone_menu_is_answered_by_pressing_the_key_not_by_talking():
    signal.alarm(120)
    try:
        tts, tr = _run_one_agent_turn(Scripted(turn("Pressing one.", "press_digits", "1")), "Press 1 for orders, press 2 for payments")
        assert any(t["text"] == "pressed keypad: 1" for t in tr)
        assert len(tts.calls) == 1                      # only the opening was spoken; the key press made no speech
    finally:
        signal.alarm(0)


@pytest.mark.skipif(not CLIP.exists(), reason="needs local test clips (kept out of git)")
def test_when_the_ai_ends_the_call_it_says_goodbye_and_closes_the_line():
    signal.alarm(120)
    try:
        tts, tr = _run_one_agent_turn(Scripted(turn("Thank you, goodbye.", "end_call")), "Your ticket number is T 55. Anything else?")
        assert tts.calls[-1][0] == "Thank you, goodbye." and any("ended by the AI" in t["text"] for t in tr)
    finally:
        signal.alarm(0)
