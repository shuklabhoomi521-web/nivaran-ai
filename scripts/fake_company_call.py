"""PRACTICE call: a pretend company phone line (menu, hold music, an agent) talks to our phone bot over the same websocket Twilio uses.
No real phone, no Twilio, no money. Computer voices come from the Mac's own `say` (free).
Run the server in practice mode first:   cd backend && PHONE_REHEARSAL=1 python -m app.voice.server
Then:                                      python scripts/fake_company_call.py
Writes docs/call-rehearsal.md (what each side said, key presses, the delays)."""
import asyncio
import audioop
import base64
import json
import math
import subprocess
import sys
import tempfile
import time
import wave
from pathlib import Path

import numpy as np
import websockets

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
BASE = "ws://localhost:7861/phone/ws"
SR = 8000


def say(text: str, voice: str) -> bytes:
    """Mac voice -> 8 kHz 16-bit mono PCM (what a phone line carries)."""
    with tempfile.TemporaryDirectory() as t:
        aiff, wav_ = Path(t) / "a.aiff", Path(t) / "a.wav"
        subprocess.run(["say", "-v", voice, "-o", str(aiff), text], check=True)
        subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16@8000", "-c", "1", str(aiff), str(wav_)], check=True)
        with wave.open(str(wav_)) as w:
            return w.readframes(w.getnframes())


def hold_music(secs: float) -> bytes:
    t = np.arange(int(secs * SR)) / SR
    notes = [440, 494, 523, 587]
    x = sum(np.sin(2 * np.pi * notes[int(i) % 4] * t) * np.exp(-((t * 2) % 1) * 2) for i in range(len(notes))) * 2500
    return x.astype("<i2").tobytes()


def goertzel(x: np.ndarray, f: float) -> float:
    k = 2 * math.cos(2 * math.pi * f / SR); s1 = s2 = 0.0
    for v in x:
        s1, s2 = v + k * s1 - s2, s1
    return s1 * s1 + s2 * s2 - k * s1 * s2


LOW, HIGH = [697, 770, 852, 941], [1209, 1336, 1477]
KEYS = {(697, 1209): "1", (697, 1336): "2", (697, 1477): "3", (770, 1209): "4", (770, 1336): "5", (770, 1477): "6",
        (852, 1209): "7", (852, 1336): "8", (852, 1477): "9", (941, 1209): "*", (941, 1336): "0", (941, 1477): "#"}


def decode_dtmf(pcm: np.ndarray) -> str | None:
    """A keypad digit if this 40 ms block is two clean tones, else None (speech does not look like this)."""
    pcm = pcm.astype(float)
    if len(pcm) < 320 or np.sqrt(np.mean(pcm ** 2)) < 800:
        return None
    x = pcm[:320] * np.hanning(320)
    lo = [goertzel(x, f) for f in LOW]; hi = [goertzel(x, f) for f in HIGH]
    total = float(np.sum(x ** 2)) * 320 / 2 + 1e-9
    if max(lo) + max(hi) < 0.6 * total or sorted(lo)[-1] < 4 * sorted(lo)[-2] or sorted(hi)[-1] < 4 * sorted(hi)[-2]:
        return None
    return KEYS[(LOW[int(np.argmax(lo))], HIGH[int(np.argmax(hi))])]


class Peer:
    def __init__(self, ws):
        self.ws, self.t0 = ws, time.time()
        self.out_pcm = bytearray()           # what the bot sent us
        self.last_sound = 0.0                # when the bot last made a sound
        self.sounds: list[float] = []        # every moment the bot made a sound (to measure how fast it answers)
        self.log: list[tuple[float, str, str]] = []
        self.digits: list[str] = []
        self._last_digit_t = -9.0

    def note(self, who, text):
        self.log.append((round(time.time() - self.t0, 1), who, text)); print(f"[{self.log[-1][0]:5.1f}s] {who:6} {text}", flush=True)

    async def reader(self):
        async for raw in self.ws:
            m = json.loads(raw)
            if m.get("event") == "media":
                pcm = audioop.ulaw2lin(base64.b64decode(m["media"]["payload"]), 2)
                x = np.frombuffer(pcm, "<i2")
                self.out_pcm += pcm
                if len(x) and np.sqrt(np.mean(x.astype(float) ** 2)) > 300:
                    self.last_sound = time.time(); self.sounds.append(self.last_sound)
                    d = decode_dtmf(x[-320:] if len(x) >= 320 else x)
                    if d and time.time() - self._last_digit_t > 0.5:
                        self._last_digit_t = time.time(); self.digits.append(d); self.note("bot", f"pressed key {d}")
            elif m.get("event") in ("clear", "stop"):
                pass

    async def play(self, pcm: bytes):
        ulaw = audioop.lin2ulaw(pcm, 2)
        for i in range(0, len(ulaw), 160):
            await self.ws.send(json.dumps({"event": "media", "streamSid": "MZrehearsal", "media": {"track": "inbound", "payload": base64.b64encode(ulaw[i:i + 160]).decode()}}))
            await asyncio.sleep(0.02)

    async def silence(self, secs):
        await self.play(b"\0\0" * int(SR * secs))

    async def wait_bot_quiet(self, quiet=1.4, timeout=40):
        """Wait until the bot has been silent for `quiet` seconds (and has said something since we last spoke)."""
        t0 = time.time()
        while time.time() - t0 < timeout:
            if self.last_sound and time.time() - self.last_sound > quiet:
                return time.time() - self.last_sound
            await self.silence(0.1)
        return None

    def first_sound_after(self, t_end):
        return next((t - t_end for t in self.sounds if t > t_end), None)

    async def wait_bot_reply(self, t_end, timeout=90, quiet=1.5):
        """Wait for the bot's FIRST sound after we stopped talking (it may be slow), then until it is quiet again. Returns the delay in seconds."""
        t0 = time.time()
        while time.time() - t0 < timeout and self.first_sound_after(t_end) is None:
            await self.silence(0.1)
        delay = self.first_sound_after(t_end)
        await self.wait_bot_quiet(quiet)
        return delay

    async def wait_for_digit(self, n_before, timeout=30):
        t0 = time.time()
        while time.time() - t0 < timeout:
            if len(self.digits) > n_before:
                return self.digits[-1]
            await self.silence(0.1)
        return None


async def main():
    import httpx
    global EV0
    old = httpx.get("http://localhost:7861/voice/events", params={"since": 0}, timeout=10).json()
    EV0 = old[-1]["n"] if old else 0
    results = {}
    async with websockets.connect(BASE, max_size=None) as ws:
        p = Peer(ws)
        reader = asyncio.create_task(p.reader())
        await ws.send(json.dumps({"event": "connected", "protocol": "Call", "version": "1.0.0"}))
        await ws.send(json.dumps({"event": "start", "sequenceNumber": "1", "streamSid": "MZrehearsal",
                                  "start": {"accountSid": "ACrehearsal", "streamSid": "MZrehearsal", "callSid": "CArehearsal", "tracks": ["inbound"],
                                            "mediaFormat": {"encoding": "audio/x-mulaw", "sampleRate": 8000, "channels": 1}, "customParameters": {}}}))
        p.note("setup", "pretend call connected; the bot should introduce itself as an AI first")
        await p.silence(1.0)
        await p.wait_bot_quiet(1.5)
        p.note("bot", "(finished its introduction)")

        async def ask_menu(text, voice="Aman", expect=None):
            n = len(p.digits)
            p.note("menu", text)
            await p.play(say(text, voice)); t_end = time.time()
            key = await p.wait_for_digit(n)
            results.setdefault('menu_delay', []).append(round(time.time() - t_end, 1))
            p.note("check", f"bot pressed {key!r}" + (f" (wanted {expect!r}: {'OK' if key == expect else 'WRONG'})" if expect else ""))
            return key, (time.time() - t_end)

        k1, d1 = await ask_menu("Welcome to Swiggy customer care. Press 1 for order issues. Press 2 for payments. Press 3 for anything else.", expect="1")
        k2, d2 = await ask_menu("For a late or cold order, press 1. For missing items, press 2. To return to the main menu, press 9.", expect="1")
        results["menu"] = (k1, k2)
        p.note("menu", "Please hold while we connect you to an agent.")
        await p.play(say("Please hold while we connect you to an agent.", "Aman"))
        spoke_before = len(p.out_pcm)
        p.note("setup", "hold music for 14 seconds")
        await p.play(hold_music(14))
        await p.silence(2.0)
        p.note("agent", "Hello, this is Priya from Swiggy support. How can I help you today?")
        await p.play(say("Hello, this is Priya from Swiggy support. How can I help you today?", "Samantha")); t1 = time.time()
        results["answer1_delay"] = round(await p.wait_bot_reply(t1) or -1, 1)
        p.note("agent", "Can you give me the order I D please?")
        await p.play(say("Can you give me the order I D please?", "Samantha")); t2 = time.time()
        results["answer2_delay"] = round(await p.wait_bot_reply(t2) or -1, 1)
        p.note("agent", "Please tell me the OTP you received on your phone.")
        await p.play(say("To verify, please tell me the O T P you received on your phone.", "Samantha")); t3 = time.time()
        results["otp_delay"] = round(await p.wait_bot_reply(t3) or -1, 1)
        p.note("agent", "I have raised a refund. Your ticket number is T 5 5 5. Anything else?")
        await p.play(say("Okay, I have raised a refund for you. Your ticket number is T 5 5 5. Is there anything else?", "Samantha")); t4 = time.time()
        results["goodbye_delay"] = round(await p.wait_bot_reply(t4) or -1, 1)
        await p.silence(3)
        reader.cancel()
    import httpx
    ev = httpx.get("http://localhost:7861/voice/events", params={"since": EV0}, timeout=10).json()
    md = ["# Practice call (pretend company, no real phone)", "", "A pretend company line (menu, hold music, an agent) called our phone bot over the same websocket Twilio uses. "
          "Computer voices from the Mac. Speech-to-text, brain and voice are the real ones configured in .env.", "",
          f"Result: {json.dumps(results)}", "", "## What the bot's side logged", ""]
    md += [f"- `{e['t']}` **{ {'heard': 'agent (heard)', 'spoke': 'AI said', 'info': 'info', 'err': 'ERROR'}.get(e['kind'], e['kind']) }**: {e['text']}" for e in ev]
    (ROOT / "docs" / "call-rehearsal.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    results["bot_audio_seconds"] = round(len(p.out_pcm) / 2 / SR, 1)
    print(json.dumps(results))
    (ROOT / "docs" / ".call-rehearsal.json").write_text(json.dumps({"results": results, "log": p.log}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    asyncio.run(main())
