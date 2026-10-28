"""Plays a recorded WAV into the running voice server over real WebRTC (like a browser would) and prints what the bot heard and said.
Usage: python experiments/voice_smoke_test.py speech_test/recordings/english/english-02.wav [en-IN] [http://localhost:7861]"""
import asyncio
import json
import sys
import time

import httpx
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRecorder

wav = sys.argv[1]
lang = sys.argv[2] if len(sys.argv) > 2 else "en-IN"
base = sys.argv[3] if len(sys.argv) > 3 else "http://localhost:7861"


async def main():
    pc = RTCPeerConnection()
    player = MediaPlayer(wav)
    pc.addTrack(player.audio)
    pc.createDataChannel("chat")
    got_audio = {"frames": 0}

    @pc.on("track")
    def on_track(track):
        async def drain():
            try:
                while True:
                    await track.recv()
                    got_audio["frames"] += 1
            except Exception:  # noqa: BLE001
                pass
        if track.kind == "audio":
            asyncio.ensure_future(drain())

    await pc.setLocalDescription(await pc.createOffer())
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(f"{base}/voice/api/offer", json={"sdp": pc.localDescription.sdp, "type": pc.localDescription.type,
                                                           "request_data": {"language": lang}})
        r.raise_for_status()
        ans = r.json()
        await pc.setRemoteDescription(RTCSessionDescription(sdp=ans["sdp"], type=ans["type"]))
        print("connected; playing your clip into the bot...", flush=True)
        since, t0, seen = 0, time.time(), []
        while time.time() - t0 < 110:
            await asyncio.sleep(1.5)
            ev = (await c.get(f"{base}/voice/events", params={"since": since})).json()
            for e in ev:
                since = e["n"]
                print(f"  [{time.time() - t0:5.1f}s] {e['kind']}: {e['text']}", flush=True)
                seen.append(e["kind"])
            if "spoke" in seen and got_audio["frames"] > 300 and time.time() - t0 > 60:
                break
    print(f"bot audio frames received back: {got_audio['frames']}")
    await pc.close()


asyncio.run(main())
