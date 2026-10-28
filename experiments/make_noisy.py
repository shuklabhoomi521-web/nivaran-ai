"""Make noisy copies of clean recordings WITHOUT downloading anything: street noise is built here from
(a) brown noise (engine/traffic rumble), (b) a few short horn-like tones, (c) market babble = several other people's
public FLEURS clips mixed together. Speech-to-noise ratio is set exactly. Usage: make_noisy.py <in.wav> <out.wav> <snr_db> <seed>"""
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def read(p):
    with wave.open(str(p), "rb") as w:
        assert w.getnchannels() == 1 and w.getsampwidth() == 2
        return np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float64) / 32768, w.getframerate()


def street(n, sr, rng):
    brown = np.cumsum(rng.standard_normal(n)); brown -= np.convolve(brown, np.ones(sr // 4) / (sr // 4), "same")   # rumble, no DC drift
    brown /= np.std(brown)
    t = np.arange(n) / sr
    horns = np.zeros(n)
    for _ in range(3):
        s = rng.integers(0, max(1, n - sr)); f = rng.choice([420, 480, 520])
        horns[s:s + sr // 2] += 0.6 * np.sin(2 * np.pi * f * t[:sr // 2]) * np.hanning(sr // 2)
    babble = np.zeros(n)
    clips = sorted((ROOT / "speech_test" / "public").glob("*/*.wav"))
    for p in rng.choice(clips, size=min(6, len(clips)), replace=False):
        x, r = read(p)
        if r != sr:
            x = np.interp(np.arange(0, len(x), r / sr), np.arange(len(x)), x)
        x = np.tile(x, n // len(x) + 1)[:n]
        babble += np.roll(x, int(rng.integers(0, n)))
    babble /= np.std(babble) + 1e-9
    return 0.8 * brown + 0.5 * horns + 0.9 * babble


def main(src, dst, snr_db, seed):
    x, sr = read(Path(src))
    rng = np.random.default_rng(int(seed))
    noise = street(len(x), sr, rng)
    rms = lambda a: np.sqrt(np.mean(a ** 2)) + 1e-12      # noqa: E731
    speech_rms = rms(x[np.abs(x) > 0.02 * np.max(np.abs(x))])     # level of the speech itself, ignoring pauses
    noise *= speech_rms / rms(noise) / (10 ** (float(snr_db) / 20))
    y = np.clip(x + noise, -1, 1)
    with wave.open(str(dst), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((y * 32767).astype("<i2").tobytes())
    print(f"{dst}: speech-to-noise {snr_db} dB")


if __name__ == "__main__":
    main(*sys.argv[1:5])
