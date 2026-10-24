"""Live test of the running voice server over real WebRTC, like a browser, but with recorded audio instead of a microphone.
Scenarios cover the four languages, a two-turn chat, talking over the bot (barge-in) and a spoken card number.
Writes docs/voice-live-test.md. Usage: python scripts/voice_live_test.py [scenario names...]   (server: python -m app.voice.server)"""
import asyncio
import json
import sys
import tempfile
import time
import wave
from pathlib import Path

import httpx
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://localhost:7861"
REC, LIVE = ROOT / "speech_test" / "recordings", ROOT / "speech_test" / "live_clips"
SILENCE_THRESHOLD = 600      # bot audio quieter than this counts as silence


def load(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as w:
        assert w.getframerate() == 16000 and w.getnchannels() == 1, path
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)


def build(parts) -> tuple[Path, list[tuple[float, float]]]:
    """parts: ('silence', secs) or ('clip', path). Returns the combined wav and the (start, end) seconds of each clip."""
    chunks, spans, t = [], [], 0.0
    for kind, val in parts:
        a = np.zeros(int(16000 * val), dtype=np.int16) if kind == "silence" else load(val)
        if kind == "clip":
            spans.append((t, t + len(a) / 16000))
        chunks.append(a)
        t += len(a) / 16000
    f = Path(tempfile.mkdtemp()) / "in.wav"
    with wave.open(str(f), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes(np.concatenate(chunks).tobytes())
    return f, spans


def segments(timeline, gap=0.6):
    """[(t, loud)] -> list of (start, end) where the bot was making sound."""
    segs, cur = [], None
    for t, loud in timeline:
        if loud:
            if cur and t - cur[1] <= gap:
                cur[1] = t
            else:
                if cur:
                    segs.append(tuple(cur))
                cur = [t, t]
    if cur:
        segs.append(tuple(cur))
    return segs


async def run(name, lang, parts, total_secs, min_replies, note=""):
    wav, spans = build(parts)
    pc = RTCPeerConnection()
    player = MediaPlayer(str(wav))
    pc.addTrack(player.audio)
    pc.createDataChannel("chat")
    timeline, clock = [], [time.time()]
    t0 = clock[0]

    @pc.on("track")
    def on_track(track):
        async def drain():
            try:
                while True:
                    fr = await track.recv()
                    arr = fr.to_ndarray().astype(np.int32).ravel()
                    timeline.append((time.time() - clock[0], int(np.abs(arr).max()) > SILENCE_THRESHOLD))
            except Exception:  # noqa: BLE001
                pass
        if track.kind == "audio":
            asyncio.ensure_future(drain())

    await pc.setLocalDescription(await pc.createOffer())
    events = []
    async with httpx.AsyncClient(timeout=30) as c:
        since = (await c.get(f"{BASE}/voice/events", params={"since": 0})).json()
        since = since[-1]["n"] if since else 0
        r = await c.post(f"{BASE}/voice/api/offer", json={"sdp": pc.localDescription.sdp, "type": pc.localDescription.type,
                                                           "request_data": {"language": lang}})
        r.raise_for_status()
        ans = r.json()
        t0 = clock[0] = time.time()      # clock zero = the moment the connection is made
        await pc.setRemoteDescription(RTCSessionDescription(sdp=ans["sdp"], type=ans["type"]))
        while time.time() - t0 < total_secs:
            await asyncio.sleep(1.0)
            for e in (await c.get(f"{BASE}/voice/events", params={"since": since})).json():
                since = e["n"]
                e["at"] = round(time.time() - t0, 1)
                events.append(e)
            if sum(1 for e in events if e["kind"] == "spoke") >= min_replies + 1 and time.time() - t0 > total_secs - 8:
                break
    await pc.close()
    return {"name": name, "lang": lang, "note": note, "events": events, "spans": spans, "bot_segments": segments(timeline)}


def first_sound_after(segs, t):
    for s, e in segs:
        if e > t:
            return max(s, t)
    return None


def scenarios():
    S = lambda s: ("silence", s)       # noqa: E731
    C = lambda p: ("clip", p)          # noqa: E731
    sc = {}
    sc["1 English, two turns (Zomato, then the order number)"] = ("en-IN", [S(9), C(REC / "english/english-01.wav"), S(22), C(LIVE / "answer_order_number.wav"), S(28)], 85, 2,
                                                              "Indian-English voice (yours) then a computer-voice answer")
    sc["2 Hinglish, one turn (Amazon, order number given)"] = ("hinglish", [S(9), C(REC / "hinglish/hinglish-04.wav"), S(30)], 60, 1, "your voice")
    sc["3 Hindi (Zomato)"] = ("hi-IN", [S(9), C(LIVE / "hindi_zomato.wav"), S(25)], 55, 1, "computer voice")
    sc["4 Tamil (Swiggy)"] = ("ta-IN", [S(9), C(LIVE / "tamil_swiggy.wav"), S(25)], 55, 1, "computer voice")
    sc["5 Talking over the bot (barge-in)"] = ("en-IN", [S(3.0), C(REC / "english/english-01.wav"), S(20)], 50, 1, "speech starts 3 s in, while the greeting is still playing")
    sc["6 Card number said aloud"] = ("en-IN", [S(9), C(LIVE / "card_test.wav"), S(25)], 60, 1, "computer voice")
    sc["7 Auto: English first, then switches to Hindi"] = ("auto", [S(9), C(REC / "english/english-01.wav"), S(20), C(LIVE / "hindi_zomato.wav"), S(30)], 85, 2,
                                                             "language switch: the second answer must be in Hindi")
    sc["8 Auto: Tamil first, then switches to English"] = ("auto", [S(9), C(LIVE / "tamil_swiggy.wav"), S(20), C(LIVE / "answer_order_number.wav"), S(30)], 85, 2,
                                                            "language switch: the second answer must be in English")
    sc["9 Tamil chosen on the page, but the person speaks English"] = ("ta-IN", [S(9), C(REC / "english/english-01.wav"), S(22), C(LIVE / "answer_order_number.wav"), S(28)], 85, 2,
                                                                      "the page language is only the starting language: answers must be in English")
    return sc


def _credit_line():
    sys.path.insert(0, str(ROOT / "backend"))
    from app.speech.credits import CreditLedger
    print(CreditLedger().session_line(), flush=True)


def main():
    want = sys.argv[1:]
    results = []
    for _ in range(60):                       # wait until the server has finished warming up
        try:
            if httpx.get(f"{BASE}/voice/ready", timeout=5).json().get("ready"):
                break
        except Exception:  # noqa: BLE001
            pass
        time.sleep(2)
    for name, (lang, parts, total, replies, note) in scenarios().items():
        if want and not any(name.startswith(w) for w in want):
            continue
        missing = [p[1] for p in parts if p[0] == "clip" and not Path(p[1]).exists()]
        if missing:
            print(f"SKIP {name}: missing {missing}")
            continue
        print(f"running: {name} ...", flush=True)
        res = asyncio.run(run(name, lang, parts, total, replies, note))
        results.append(res)
        for e in res["events"]:
            print(f"   [{e['at']:5.1f}s] {e['kind']:5} {e['text'][:110]}" + (f"  ({e['secs']}s)" if e.get('secs') else ""), flush=True)
        print(f"   user clip(s) at {[(round(a, 1), round(b, 1)) for a, b in res['spans']]}; bot made sound at {[(round(a, 1), round(b, 1)) for a, b in res['bot_segments']]}", flush=True)
    (ROOT / "docs" / ".voice-live-test.json").write_text(json.dumps(results, ensure_ascii=False, indent=1))
    write_report(results)
    _credit_line()


def write_report(results):
    md = ["# Voice bot live test", "",
          "Recorded audio is played into the running voice server over real WebRTC (like a browser). Computer voices are marked. "
          "Latency = from the end of the person's sentence to the first sound the bot makes in reply (measured on the audio the client receives).", "",
          "| Scenario | Heard (speech-to-text) | Understood | Bot said | Delay to first sound |", "|---|---|---|---|---|"]
    for r in results:
        ev = r["events"]
        heard = [e for e in ev if e["kind"] == "heard"]
        notes = [e for e in ev if e["kind"] == "note"]
        spoke = [e for e in ev if e["kind"] == "spoke"][1:]            # skip the greeting
        delays = []
        for _a, end in r["spans"]:
            t = first_sound_after(r["bot_segments"], end)
            delays.append("-" if t is None else f"{t - end:.1f} s")
        md.append(f"| {r['name']} ({r['note']}) | " + "<br>".join(e["text"][:90] for e in heard) + " | "
                  + "<br>".join(e["text"][:90] for e in notes) + " | " + "<br>".join(e["text"][:80] for e in spoke) + " | " + ", ".join(delays) + " |")
    (ROOT / "docs" / "voice-live-test.md").write_text("\n".join(md) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
