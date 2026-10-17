"""Pick a few real-human clips from the downloaded Google FLEURS dev files (CC-BY-4.0) for the speech bake-off.

Reads speech_test/_download/<lang>/dev.tsv + dev.tar.gz, picks N clips of 5-11 seconds (fixed random seed), writes them as
speech_test/public/<language>/<id>.wav with the exact reference text in speech_test/public/references.json.
Clip 5 of each language also gets a NOISY copy: other speakers' voices mixed in as background chatter (babble) at 10 dB
signal-to-noise. That noise is synthetic (made from other FLEURS speakers), and the report says so.
Usage: python scripts/prepare_public_clips.py [--n 5]
"""
import argparse
import csv
import io
import json
import random
import tarfile
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DL = ROOT / "speech_test" / "_download"
OUT = ROOT / "speech_test" / "public"
LANGS = {"hindi": "hi_in", "tamil": "ta_in", "english": "en_us"}
SEED, SNR_DB = 17, 10


def read_wav(b: bytes) -> tuple[np.ndarray, int]:
    """FLEURS clips are 32-bit float WAV; convert to 16-bit mono 16 kHz with macOS afconvert first."""
    import subprocess, tempfile
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = Path(tmp) / "in.wav", Path(tmp) / "out.wav"
        src.write_bytes(b)
        subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16@16000", "-c", "1", str(src), str(dst)], check=True, capture_output=True)
        b = dst.read_bytes()
    with wave.open(io.BytesIO(b), "rb") as w:
        assert w.getnchannels() == 1 and w.getsampwidth() == 2
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32), w.getframerate()


def write_wav(path: Path, x: np.ndarray, rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes(np.clip(x, -32768, 32767).astype(np.int16).tobytes())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5)
    n = ap.parse_args().n
    refs: dict = {}
    rng = random.Random(SEED)
    for lang, code in LANGS.items():
        rows = list(csv.reader((DL / code / "dev.tsv").open(encoding="utf-8"), delimiter="\t"))
        # columns: id, file_name, raw_transcription, transcription, characters, num_samples, gender
        cand = [r for r in rows if len(r) >= 7 and 80000 <= int(r[5]) <= 176000]
        rng.shuffle(cand)
        picks = cand[:n]
        babble_names = [r[1] for r in cand[n:n + 4]]
        want = {r[1] for r in picks} | set(babble_names)
        found = {}
        with tarfile.open(DL / code / "dev.tar.gz", "r:gz") as tf:
            for m in tf:
                base = Path(m.name).name
                if m.isfile() and base in want:
                    found[base] = tf.extractfile(m).read()
                    if len(found) == len(want):
                        break
        missing = want - set(found)
        assert not missing, f"{lang}: not found in tar: {missing}"
        babble_src = [read_wav(found[b])[0] for b in babble_names]
        refs[lang] = []
        for i, r in enumerate(picks, 1):
            x, rate = read_wav(found[r[1]])
            cid = f"{lang}-fleurs-{i:02d}"
            write_wav(OUT / lang / f"{cid}.wav", x, rate)
            refs[lang].append({"id": cid, "text": r[2], "noisy": False, "source": f"FLEURS {code} dev {r[1]}", "gender": r[6]})
            if i == n:   # the last clip also gets a noisy copy
                bab = np.zeros_like(x)
                for s in babble_src:
                    s = np.resize(s, x.shape)
                    bab += s
                p_sig, p_noise = float(np.mean(x ** 2)), float(np.mean(bab ** 2)) or 1.0
                bab *= (p_sig / (p_noise * 10 ** (SNR_DB / 10))) ** 0.5
                nid = f"{lang}-fleurs-noisy-{i:02d}"
                write_wav(OUT / lang / f"{nid}.wav", x + bab, rate)
                refs[lang].append({"id": nid, "text": r[2], "noisy": True,
                                   "source": f"FLEURS {code} dev {r[1]} + synthetic babble at {SNR_DB} dB SNR", "gender": r[6]})
        print(lang, [c["id"] for c in refs[lang]])
    (OUT / "references.json").write_text(json.dumps(refs, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "LICENSE.txt").write_text("Clips are from Google FLEURS (https://huggingface.co/datasets/google/fleurs), licensed CC-BY-4.0.\n"
                                     "Credit: Conneau et al., 'FLEURS: Few-shot Learning Evaluation of Universal Representations of Speech'.\n")


if __name__ == "__main__":
    main()
