"""Practice the PHONE CALL in the browser path with computer-voice agent clips (no human needed). Needs the server running:
   cd backend && python -m app.voice.server        (STT_PROVIDER=local in .env keeps it free)
Then:  python scripts/browser_call_test.py"""
import asyncio
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import voice_live_test as v  # noqa: E402

CLIPS = {
    "a1": ("Yes, go ahead. This is Priya from Swiggy support. Please tell me the problem.", "Samantha"),
    "a2": ("For order issues, press 1. For payments, press 2. For anything else, press 3.", "Samantha"),
    "a3": ("Can you give me the order I D please?", "Samantha"),
    "a4": ("To verify, please tell me the O T P you received on your phone.", "Samantha"),
    "a5": ("Okay, I have raised a refund. Your ticket number is T 5 5 5. Is there anything else?", "Samantha"),
}


def make(name, text, voice) -> Path:
    out = v.LIVE / f"agent_{name}.wav"
    if not out.exists():
        with tempfile.TemporaryDirectory() as t:
            aiff = Path(t) / "a.aiff"
            subprocess.run(["say", "-v", voice, "-o", str(aiff), text], check=True)
            subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16@16000", "-c", "1", str(aiff), str(out)], check=True)
    return out


def main():
    clips = {k: make(k, *val) for k, val in CLIPS.items()}
    S, C = (lambda s: ("silence", s)), (lambda p: ("clip", p))      # noqa: E731
    parts = [S(10), C(clips["a1"]), S(24), C(clips["a2"]), S(24), C(clips["a3"]), S(24), C(clips["a4"]), S(24), C(clips["a5"]), S(26)]
    res = asyncio.run(v.run("browser phone call practice", "en-IN", parts, 190, 5, "agent = computer voice, phone-quality line", extra={"mode": "phone"}))
    for e in res["events"]:
        print(f"[{e['at']:6.1f}s] {e['kind']:6} {e['text'][:140]}")
    delays = []
    for _a, end in res["spans"]:
        t = v.first_sound_after(res["bot_segments"], end)
        delays.append("-" if t is None else round(t - end, 1))
    print("delay from each agent line to the AI's first sound (s):", delays)


if __name__ == "__main__":
    main()
