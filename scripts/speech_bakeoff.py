"""Speech bake-off: how well does the speech provider hear Tamil, Hindi, Hinglish and English?

Two tests, each heard 3 ways (clean 16 kHz, phone 8 kHz, phone 8 kHz mu-law):
  REAL = real human voices, counted MORE (70%):
         OWN    = your own recordings in speech_test/recordings/<language>/<language>-NN.(m4a|wav|mp3|aiff|caf)
         PUBLIC = real clips from Google FLEURS (CC-BY-4.0) in speech_test/public/ (see scripts/prepare_public_clips.py)
  SYNTH = text-to-speech voice reading the same sentences, heard back by speech-to-text   (30%: synthetic voices are too clean)
Same slow-down and caching as Phase 1: answers are cached, so a re-run only makes new calls, and it stops cleanly at a daily limit.

Usage: python scripts/speech_bakeoff.py [--only synth|real] [--langs english,hindi] [--no-tts-samples]
"""
import argparse
import hashlib
import json
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.brain.ratelimit import DailyQuotaExceeded  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.speech.audio import CONDITIONS, render  # noqa: E402
from app.speech.base import SpeechError  # noqa: E402
from app.speech.factory import make_stt, make_tts  # noqa: E402
from app.speech.scoring import cer, digits_in, normalize, wer  # noqa: E402

TEST_DIR = ROOT / "speech_test"
REC_DIR = TEST_DIR / "recordings"
TTS_DIR = TEST_DIR / "tts_samples"
CACHE = ROOT / "docs" / ".speech-cache.json"
OUT_MD = ROOT / "docs" / "speech-bakeoff.md"
OUT_JSON = ROOT / "docs" / "speech-bakeoff.json"
AUDIO_EXT = (".m4a", ".wav", ".mp3", ".aiff", ".aif", ".caf")
W_OWN, W_SYNTH = 0.7, 0.3


def load_cache() -> dict:
    return json.loads(CACHE.read_text()) if CACHE.exists() else {}


def save_cache(c: dict) -> None:
    CACHE.write_text(json.dumps(c, ensure_ascii=False))


def find_recording(lang: str, sid: str) -> Path | None:
    for ext in AUDIO_EXT:
        p = REC_DIR / lang / f"{sid}{ext}"
        if p.exists():
            return p
    return None


def best_score(sent: dict, hyp: str) -> tuple[float, float]:
    """Hinglish may come back in Roman or Devanagari letters: score against both, keep the better."""
    refs = [sent["text"]] + ([sent["text_alt"]] if sent.get("text_alt") else [])
    return min(wer(r, hyp) for r in refs), min(cer(r, hyp) for r in refs)


def keep_awake() -> None:
    """Stop the Mac from sleeping while this script runs (a sleeping laptop stalled earlier runs)."""
    import os
    import shutil
    import subprocess
    if shutil.which("caffeinate"):
        subprocess.Popen(["caffeinate", "-i", "-w", str(os.getpid())], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main() -> None:
    keep_awake()
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["synth", "real", "own", "public"])
    ap.add_argument("--langs")
    ap.add_argument("--no-tts-samples", action="store_true")
    args = ap.parse_args()
    s = get_settings()
    sentences = json.loads((TEST_DIR / "sentences.json").read_text())
    langs = args.langs.split(",") if args.langs else list(sentences)
    stt, tts = make_stt(), make_tts()
    cache = load_cache()
    rows = []
    stopped = None
    stt_id = f"{s.stt_provider}:{s.gemini_stt_model}"

    def transcribe(audio_wav: bytes, key_extra: str):
        key = hashlib.sha1(audio_wav).hexdigest() + "|" + stt_id + "|" + key_extra
        if key in cache:
            return cache[key]["text"], cache[key]["secs"], True
        t0 = time.time()
        try:
            text = stt.transcribe(audio_wav, "audio/wav").text
        except SpeechError as e:     # hung or failed call: counts as a miss, and is remembered so we do not retry forever
            text = f"[FAILED: {e}]"
        secs = round(time.time() - t0, 2)
        cache[key] = {"text": text, "secs": secs}
        save_cache(cache)
        return text, secs, False

    public_refs = {}
    pr = TEST_DIR / "public" / "references.json"
    if pr.exists():
        public_refs = json.loads(pr.read_text(encoding="utf-8"))

    def run_clip(lang, sent, kind, path):
        for cond in CONDITIONS:
            hyp, secs, cached = transcribe(render(path, cond), "")
            w, c = best_score(sent, hyp)
            rows.append({"lang": lang, "id": sent["id"], "kind": kind, "cond": cond, "noisy": bool(sent.get("noisy")),
                         "wer": round(w, 3), "cer": round(c, 3), "secs": secs, "ref": sent["text"], "hyp": hyp,
                         "digits_ok": None})
            print(f"  {kind:6} {sent['id']} {cond:11} WER {w:.2f} CER {c:.2f} ({'cached' if cached else str(secs) + 's'})", flush=True)

    try:
        if args.only in (None, "real", "public"):
            for lang in langs:
                for clip in public_refs.get(lang, []):
                    run_clip(lang, clip, "public", TEST_DIR / "public" / lang / f"{clip['id']}.wav")
        for lang in langs:
            if args.only == "public":
                break
            for sent in sentences[lang]["sentences"]:
                sid = sent["id"]
                sources = []
                if args.only not in ("own", "real"):
                    wav = TTS_DIR / lang / f"{sid}.wav"
                    if not wav.exists():
                        wav.parent.mkdir(parents=True, exist_ok=True)
                        t0 = time.time()
                        audio = tts.synthesize(sent.get("tts_text", sent["text"]), sentences[lang]["locale"])
                        wav.write_bytes(audio.data)
                        print(f"  TTS {sid}: {round(time.time() - t0, 1)}s", flush=True)
                    sources.append(("synth", wav))
                if args.only not in ("synth", "public"):
                    rec = find_recording(lang, sid)
                    if rec:
                        sources.append(("own", rec))
                for kind, path in sources:
                    for cond in CONDITIONS:
                        hyp, secs, cached = transcribe(render(path, cond), "")
                        w, c = best_score(sent, hyp)
                        rows.append({"lang": lang, "id": sid, "kind": kind, "cond": cond, "noisy": bool(sent.get("noisy")),
                                     "wer": round(w, 3), "cer": round(c, 3), "secs": secs, "ref": sent["text"], "hyp": hyp,
                                     "digits_ok": (digits_in(sent["text"]) == digits_in(hyp)) if "order number" in sent["text"].lower() or "नंबर" in sent["text"] or "எண்" in sent["text"] else None})
                        print(f"  {kind:5} {sid} {cond:11} WER {w:.2f} CER {c:.2f} ({'cached' if cached else str(secs) + 's'})", flush=True)
    except DailyQuotaExceeded as e:
        stopped = str(e)
        print("STOPPED:", e)

    report(rows, s, stopped, langs)


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def pct(x):
    return "-" if x is None else f"{x:.0%}"


def report(rows, s, stopped, langs) -> None:
    def avg(lang, kind, cond, key="wer", noisy=None):
        kinds = ("own", "public") if kind == "real" else (kind,)
        xs = [r[key] for r in rows if r["lang"] == lang and r["kind"] in kinds and r["cond"] == cond
              and (noisy is None or r["noisy"] == noisy)]
        return mean(xs)

    md = ["# Speech bake-off (Phase 3)", "",
          f"- Date: {date.today()}; STT `{s.stt_provider}:{s.gemini_stt_model}`; TTS `{s.tts_provider}:{s.gemini_tts_model}`, voice `{s.gemini_tts_voice}`",
          f"- WER = word error rate (lower is better; 0% perfect). Weighted score = {int(W_OWN * 100)}% real human voices (your recordings + public FLEURS clips) + {int(W_SYNTH * 100)}% synthetic round trip "
          "(if a language has no real voices yet, only the synthetic number is shown and marked).",
          "- Conditions: clean = 16 kHz; phone 8 kHz = phone sampling rate; phone mu-law = 8 kHz squeezed like a real phone line.", ""]
    if stopped:
        md += [f"- **Stopped early:** {stopped} Run again later to continue (answers are cached).", ""]
    md += ["## Real voices vs computer voices (word error rate, lower is better)", "",
           "| Language | Condition | Real voices (own + public) | Computer voices (round trip) |", "|---|---|---|---|"]
    for lang in langs:
        for cond in CONDITIONS:
            rv, cv = avg(lang, "real", cond), avg(lang, "synth", cond)
            if rv is None and cv is None:
                continue
            md.append(f"| {lang} | {cond} | {pct(rv) if rv is not None else 'no real clips yet'} | {pct(cv)} |")
    md += ["", "## Weighted word error rate by language and condition", "",
           "| Language | Clean | Phone 8 kHz | Phone mu-law | Based on |", "|---|---|---|---|---|"]
    summary = {}
    for lang in langs:
        cells, basis = [], set()
        for cond in CONDITIONS:
            own, syn = avg(lang, "real", cond), avg(lang, "synth", cond)
            if own is not None and syn is not None:
                v = W_OWN * own + W_SYNTH * syn
                basis.add("real voices + synthetic")
            elif own is not None:
                v = own
                basis.add("real voices only")
            elif syn is not None:
                v = syn
                basis.add("synthetic only (NO real voices for this language yet)")
            else:
                v = None
            summary[(lang, cond)] = v
            cells.append(pct(v))
        md.append(f"| {lang} | {cells[0]} | {cells[1]} | {cells[2]} | {', '.join(sorted(basis)) or 'no data'} |")
    for kind, title in (("own", "Your own recordings only"), ("public", "Public real-voice clips only (Google FLEURS: longer, formal read sentences; the noisy copy has synthetic chatter added)"), ("synth", "Synthetic round trip only")):
        md += ["", f"## {title}: WER / CER", "", "| Language | Condition | WER | CER | Noisy clip WER |", "|---|---|---|---|---|"]
        for lang in langs:
            for cond in CONDITIONS:
                w, c = avg(lang, kind, cond), avg(lang, kind, cond, "cer")
                if w is None:
                    continue
                md.append(f"| {lang} | {cond} | {pct(w)} | {pct(c)} | {pct(avg(lang, kind, cond, 'wer', True))} |")
    secs = [r["secs"] for r in rows if r["secs"] and r["secs"] > 0]
    if secs:
        secs.sort()
        md += ["", f"## Speed of the speech-to-text call (non-streaming): median {secs[len(secs) // 2]:.1f}s, slowest {secs[-1]:.1f}s ({len(secs)} calls)"]
    dg = [r for r in rows if r["digits_ok"] is not None]
    if dg:
        md += ["", "## Order-number sentence: digits heard exactly?", "", "| Language | Source | Condition | Digits right |", "|---|---|---|---|"]
        md += [f"| {r['lang']} | {r['kind']} | {r['cond']} | {'yes' if r['digits_ok'] else 'NO: heard ' + repr(r['hyp'])} |" for r in dg]
    worst = sorted(rows, key=lambda r: -r["wer"])[:8]
    md += ["", "## Worst 8 clips (what was said vs what was heard)", "", "| Clip | Source | Condition | WER | Reference | Heard |", "|---|---|---|---|---|---|"]
    md += [f"| {r['id']} | {r['kind']} | {r['cond']} | {pct(r['wer'])} | {r['ref']} | {r['hyp']} |" for r in worst]
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    OUT_JSON.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n" + "\n".join(md))


if __name__ == "__main__":
    main()
