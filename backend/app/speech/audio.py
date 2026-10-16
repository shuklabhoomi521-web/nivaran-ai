"""Audio conversion with macOS `afconvert` (already on every Mac; reads wav, m4a, mp3, aiff, caf).
Three listening conditions: clean (16 kHz), phone_8k (8 kHz) and phone_mulaw (8 kHz, mu-law squeezed like a real phone line)."""
import shutil
import subprocess
import tempfile
from pathlib import Path

CONDITIONS = ("clean", "phone_8k", "phone_mulaw")


class AudioError(RuntimeError):
    pass


def _afconvert(src: Path, dst: Path, fmt: str) -> None:
    exe = shutil.which("afconvert")
    if not exe:
        raise AudioError("afconvert not found: audio conversion needs macOS (or install ffmpeg and extend audio.py).")
    r = subprocess.run([exe, "-f", "WAVE", "-d", fmt, "-c", "1", str(src), str(dst)], capture_output=True, text=True)
    if r.returncode != 0:
        raise AudioError(f"afconvert failed for {src.name}: {r.stderr.strip()[:200]}")


def render(src: Path, condition: str) -> bytes:
    """Return WAV bytes (mono, 16-bit) of `src` as heard under `condition`."""
    if condition not in CONDITIONS:
        raise ValueError(condition)
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        if condition == "clean":
            _afconvert(src, t / "o.wav", "LEI16@16000")
        elif condition == "phone_8k":
            _afconvert(src, t / "o.wav", "LEI16@8000")
        else:
            _afconvert(src, t / "mu.wav", "ulaw@8000")      # squeeze like a phone line
            _afconvert(t / "mu.wav", t / "o.wav", "LEI16@8000")  # back to plain PCM so every provider can read it
        return (t / "o.wav").read_bytes()
