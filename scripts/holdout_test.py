"""The new-clips (holdout) test: run ONCE, frozen settings, no tuning afterwards (see docs/speech-settings-frozen.md).
Each founder recording is heard clean, with artificial street noise (8 dB), and as a phone call (8 kHz mu-law).
Both providers hear it with language = auto (what the live voice bot does). Long clips are cut at the quietest point (limit ~25 s per call).
Usage: python scripts/holdout_test.py [sarvam gemini groq]   (default: sarvam gemini; a third provider can be added later and gets its own result file)"""
import io
import json
import sys
import tempfile
import time
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.speech.audio import render  # noqa: E402
from app.speech.factory import _stt  # noqa: E402
from app.speech.scoring import cer, numbers_in, wer  # noqa: E402

H = ROOT / "speech_test" / "holdout"
NAMES = {"sarvam": ("Sarvam", "sarvam"), "gemini": ("Gemini", "gemini_prompt"), "groq": ("Groq Whisper", "groq"), "local": ("Local Hindi2Hinglish", "local")}


def cut(path: Path, maxs=22):
    w = wave.open(str(path)); sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), "<i2"); out = []; start = 0
    while len(x) - start > maxs * sr:
        lo, hi = start + int((maxs - 8) * sr), start + int(maxs * sr)
        k = np.convolve(np.abs(x[lo:hi]).astype(float), np.ones(sr // 10) / (sr // 10), "same").argmin()
        out.append(x[start:lo + k]); start = lo + k
    out.append(x[start:]); return out, sr


def wav(a, sr):
    b = io.BytesIO(); w = wave.open(b, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(a.tobytes()); w.close(); return b.getvalue()


def hear(provider, path: Path, condition: str):
    parts, sr = cut(path); texts = []
    for p in parts:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "c.wav"; src.write_bytes(wav(p, sr))
            audio = render(src, condition)
        texts.append(provider.transcribe(audio, "audio/wav", "auto").text)
    return " ".join(texts)


def main():
    refs = json.loads((H / "sentences.json").read_text())
    wanted = sys.argv[1:] or ["sarvam", "gemini"]
    providers = {NAMES[w][0]: _stt(NAMES[w][1]) for w in wanted}
    OUT = ROOT / "docs" / ("holdout-result.md" if wanted == ["sarvam", "gemini"] else f"holdout-result-{'-'.join(wanted)}.md")
    variants = [("clean", "{i}.wav", "clean"), ("noisy 8 dB", "{i}_noisy.wav", "clean"), ("phone mu-law", "{i}.wav", "phone_mulaw")]
    rows, raw = [], {}
    for i, ref in refs.items():
        for label, pat, cond in variants:
            for name, prov in providers.items():
                try:
                    text = hear(prov, H / pat.format(i=i), cond); err = ""
                except Exception as e:  # noqa: BLE001
                    text, err = "", f"{type(e).__name__}: {str(e)[:60]}"
                nums = numbers_in(text)
                ok = [n for n in ref["numbers"] if any(n == m or n in m for m in nums)]
                comp = [c for c in ref["companies"] if c.lower().replace("'", "") in text.lower().replace("'", "")]
                rows.append((i, label, name, wer(ref["text"], text) if not err else None, cer(ref["text"], text) if not err else None,
                             f"{len(ok)}/{len(ref['numbers'])}", f"{len(comp)}/{len(ref['companies'])}", err))
                raw[f"{i}|{label}|{name}"] = text
                print(rows[-1], flush=True); time.sleep(1)
    md = ["# New-clips (holdout) test", "", "Run once on 2026-10-23 with frozen settings, language = auto. Reference text = what the founder confirmed they said. "
          "The first draft of the reference came from Sarvam (founder corrected it), so Sarvam may look slightly better than it is. "
          "Noise is artificial (traffic rumble, horns, market babble), not a real street.", "",
          "| Clip | Condition | Provider | WER | CER | Numbers right | Company right | Problem |", "|---|---|---|---|---|---|---|---|"]
    for i, label, name, w, c, n, co, err in rows:
        md.append(f"| {i} | {label} | {name} | {'-' if w is None else f'{w:.2f}'} | {'-' if c is None else f'{c:.2f}'} | {n} | {co} | {err} |")
    for name in providers:
        ws = [r[3] for r in rows if r[2] == name and r[3] is not None]
        md.append(f"\n**{name} average WER: {np.mean(ws):.2f}** over {len(ws)} variants" if ws else f"\n**{name}: no result**")
    OUT.write_text("\n".join(md) + "\n", encoding="utf-8")
    from app.speech.credits import CreditLedger
    print(CreditLedger().session_line(), flush=True)
    (H / f"raw_transcripts_{'-'.join(wanted)}.json").write_text(json.dumps(raw, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
