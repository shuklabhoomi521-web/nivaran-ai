"""Speech bake-off: how well does the speech provider hear Hinglish, Indian English, Hindi and Tamil?

Every clip is heard 3 ways: clean (16 kHz), phone 8 kHz, and phone mu-law (8 kHz squeezed like a real phone line).
Three kinds of clips:
  OWN    = your own recordings: speech_test/recordings/<language>/<language>-NN.(wav|m4a|aac|mp3|aiff|caf)
  PUBLIC = real human clips from Google FLEURS (CC-BY-4.0): speech_test/public/ (made by scripts/prepare_public_clips.py)
  SYNTH  = a computer voice reads the sentences and the speech-to-text hears them back (too clean, so it counts less)
Answers are cached (a re-run only makes the missing calls), calls are slowed to the free limits, the Mac is kept awake,
and a hung call becomes a recorded failure instead of freezing the run.

Usage: python scripts/speech_bakeoff.py [--hint] [--only synth|real|own|public] [--langs english,hindi]
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
from app.speech.scoring import cer, numbers_in, wer, wer_inside  # noqa: E402

TEST_DIR = ROOT / "speech_test"
REC_DIR = TEST_DIR / "recordings"
TTS_DIR = TEST_DIR / "tts_samples"
CACHE = ROOT / "docs" / ".speech-cache.json"
OUT_MD = ROOT / "docs" / "speech-bakeoff.md"
OUT_JSON = ROOT / "docs" / "speech-bakeoff.json"
AUDIO_EXT = (".wav", ".m4a", ".aac", ".mp3", ".aiff", ".aif", ".caf")
W_REAL, W_SYNTH = 0.7, 0.3
LANG_HINT = {"english": "en-IN", "hindi": "hi-IN", "tamil": "ta-IN", "hinglish": "hinglish"}
COND_LABEL = {"clean": "Clean", "phone_8k": "Phone 8 kHz", "phone_mulaw": "Phone mu-law"}
REAL_GROUPS = [("hinglish", "own", "Hinglish (your recordings)"), ("english", "own", "Indian English (your recordings)"),
               ("hindi", "public", "Hindi (FLEURS, real voices)"), ("tamil", "public", "Tamil (FLEURS, real voices)"),
               ("english", "public", "US English (FLEURS, real voices)")]
SYNTH_LABEL = {"hinglish": "Hinglish", "english": "English", "hindi": "Hindi", "tamil": "Tamil"}


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


def best_scores(sent: dict, hyp: str) -> tuple[float, float, float]:
    """Hinglish may come back in Roman or Devanagari letters: score against both, keep the better."""
    refs = [sent["text"]] + ([sent["text_alt"]] if sent.get("text_alt") else [])
    return (min(wer(r, hyp) for r in refs), min(wer_inside(r, hyp) for r in refs), min(cer(r, hyp) for r in refs))


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
    ap.add_argument("--hint", action="store_true", help="tell the speech-to-text which language the user picked (the app will know this)")
    args = ap.parse_args()
    s = get_settings()
    sentences = json.loads((TEST_DIR / "sentences.json").read_text(encoding="utf-8"))
    langs = args.langs.split(",") if args.langs else list(sentences)
    stt, tts = make_stt(), make_tts()
    cache, rows, stopped = load_cache(), [], None
    stt_model = {"gemini_prompt": s.gemini_prompt_stt_model, "sarvam": s.sarvam_stt_model}.get(s.stt_provider, s.gemini_stt_model)
    stt_id = f"{s.stt_provider}:{stt_model}"

    def transcribe(audio_wav: bytes, lang: str):
        hint = LANG_HINT.get(lang) if args.hint else None
        key = hashlib.sha1(audio_wav).hexdigest() + "|" + stt_id + "|" + (f"hint={hint}" if hint else "")
        if key in cache:
            return cache[key]["text"], cache[key]["secs"], True
        t0 = time.time()
        try:
            text = stt.transcribe(audio_wav, "audio/wav", hint).text
        except SpeechError as e:
            text = f"[FAILED: {e}]"
        secs = round(time.time() - t0, 2)
        if not text.startswith("[FAILED"):     # never remember a failure: a re-run should try again
            cache[key] = {"text": text, "secs": secs}
            save_cache(cache)
        return text, secs, False

    def run_clip(lang, sent, kind, path):
        for cond in CONDITIONS:
            hyp, secs, cached = transcribe(render(path, cond), lang)
            w, w_in, c = best_scores(sent, hyp)
            exp = sent.get("numbers")
            rows.append({"lang": lang, "id": sent["id"], "kind": kind, "cond": cond,
                         "noisy": bool(sent.get("noisy")) and kind != "synth", "wer": round(w, 3), "wer_inside": round(w_in, 3),
                         "cer": round(c, 3), "secs": secs, "ref": sent["text"], "hyp": hyp, "expected_numbers": exp,
                         "numbers_ok": (all(n in numbers_in(hyp) for n in exp) if exp else None), "heard_numbers": numbers_in(hyp)})
            print(f"  {kind:6} {sent['id']} {cond:11} WER {w:.2f} (inside {w_in:.2f}) CER {c:.2f} ({'cached' if cached else str(secs) + 's'})", flush=True)

    public_refs = {}
    pr = TEST_DIR / "public" / "references.json"
    if pr.exists():
        public_refs = json.loads(pr.read_text(encoding="utf-8"))
    try:
        for lang in langs:
            if args.only in (None, "real", "own"):
                for sent in sentences[lang]["sentences"]:
                    rec = find_recording(lang, sent["id"])
                    if rec:
                        run_clip(lang, sent, "own", rec)
            if args.only in (None, "real", "public"):
                for clip in public_refs.get(lang, []):
                    run_clip(lang, clip, "public", TEST_DIR / "public" / lang / f"{clip['id']}.wav")
            if args.only in (None, "synth"):
                for sent in sentences[lang]["sentences"]:
                    wav = TTS_DIR / lang / f"{sent['id']}.wav"
                    if not wav.exists():
                        wav.parent.mkdir(parents=True, exist_ok=True)
                        t0 = time.time()
                        wav.write_bytes(tts.synthesize(sent.get("tts_text", sent["text"]), sentences[lang]["locale"]).data)
                        print(f"  TTS {sent['id']}: {round(time.time() - t0, 1)}s", flush=True)
                    run_clip(lang, sent, "synth", wav)
    except DailyQuotaExceeded as e:
        stopped = str(e)
        print("STOPPED:", e)
    report(rows, s, stt_id, args.hint, stopped)


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def pct(x):
    return "-" if x is None else f"{x:.0%}"


def report(rows, s, stt_id, hint, stopped) -> None:
    def avg(pred, cond, key="wer"):
        return mean([r[key] for r in rows if r["cond"] == cond and pred(r)])

    def real(lang, kind, noisy):
        return lambda r: r["lang"] == lang and r["kind"] == kind and r["noisy"] == noisy

    md = ["# Speech bake-off (Phase 3)", "",
          f"- Date: {date.today()}; speech-to-text `{stt_id}`; text-to-speech `{s.tts_provider}:{s.gemini_tts_model}` (voice `{s.gemini_tts_voice}`)",
          f"- Language hint given to the speech-to-text: {'YES (the app knows the language the user picked)' if hint else 'no'}",
          "- Numbers are WORD ERROR RATE (WER): lower is better, 0% is perfect. Phone 8 kHz = telephone sampling rate. mu-law = 8 kHz squeezed like a real phone line.",
          "- 'Two thousand' and '2000', or 'forty' and '40', count as the same when scoring words; the number check below is strict.", ""]
    if stopped:
        md += [f"- **Stopped early:** {stopped} Run again later to continue (answers are cached).", ""]

    md += ["## 1. Real voices, quiet clips (word error rate)", "",
           "For your own clips the second number ignores extra words you spoke around the sentence (see table 5).", "",
           "| Voices | Clips | " + " | ".join(COND_LABEL.values()) + " |", "|---|---|---|---|---|"]
    for lang, kind, label in REAL_GROUPS:
        n = len({r["id"] for r in rows if real(lang, kind, False)(r)})
        if n:
            def cell(c, lang=lang, kind=kind):
                a = pct(avg(real(lang, kind, False), c))
                return f"{a} (sentence inside: {pct(avg(real(lang, kind, False), c, 'wer_inside'))})" if kind == "own" else a
            md.append(f"| {label} | {n} | " + " | ".join(cell(c) for c in CONDITIONS) + " |")
    md += ["", "## 2. Computer voices (a computer voice reads the sentence, the speech-to-text hears it back)", "",
           "| Language | Clips | " + " | ".join(COND_LABEL.values()) + " |", "|---|---|---|---|---|"]
    for lang in SYNTH_LABEL:
        pred = lambda r, lang=lang: r["lang"] == lang and r["kind"] == "synth"  # noqa: E731
        n = len({r["id"] for r in rows if pred(r)})
        if n:
            md.append(f"| {SYNTH_LABEL[lang]} | {n} | " + " | ".join(pct(avg(pred, c)) for c in CONDITIONS) + " |")
    md += ["", "## 3. Noisy clips (real voices only, shown separately)", "",
           "| Voices | " + " | ".join(COND_LABEL.values()) + " | What the noise is |", "|---|---|---|---|---|"]
    for lang, kind, label in REAL_GROUPS:
        if any(real(lang, kind, True)(r) for r in rows):
            what = "your recording with real background noise" if kind == "own" else "FLEURS clip + synthetic chatter at 10 dB"
            md.append(f"| {label} | " + " | ".join(pct(avg(real(lang, kind, True), c)) for c in CONDITIONS) + f" | {what} |")

    md += ["", "## 4. One score per language: 70% real voices + 30% computer voices (quiet clips)", "",
           "| Language | " + " | ".join(COND_LABEL.values()) + " |", "|---|---|---|---|"]
    for lang, kind, label in REAL_GROUPS:
        if kind == "public" and lang == "english":
            continue
        cells = []
        for c in CONDITIONS:
            rv, sv = avg(real(lang, kind, False), c), avg(lambda r, lang=lang: r["lang"] == lang and r["kind"] == "synth", c)
            cells.append(pct(W_REAL * rv + W_SYNTH * sv) if rv is not None and sv is not None else (pct(sv) + " (computer voice only)" if sv is not None else "-"))
        md.append(f"| {label.split(' (')[0]} | " + " | ".join(cells) + " |")

    own_rows = [r for r in rows if r["kind"] == "own"]
    if own_rows:
        md += ["", "## 5. Your own clips, one by one (WER, and WER of the sentence found inside what was heard)", "",
               "The second number ignores extra words spoken before or after the sentence (for example 'Hello, haan ji...'). "
               "A big gap means you said more than the listed sentence, not that the speech-to-text was wrong.", "",
               "| Clip | Noise | Clean | Phone 8 kHz | Phone mu-law | Heard (clean) |", "|---|---|---|---|---|---|"]
        for cid in dict.fromkeys(r["id"] for r in own_rows):
            by = {r["cond"]: r for r in own_rows if r["id"] == cid}
            cell = lambda c: f"{pct(by[c]['wer'])} / {pct(by[c]['wer_inside'])}" if c in by else "-"  # noqa: E731
            md.append(f"| {cid} | {'noisy' if by['clean']['noisy'] else ''} | {cell('clean')} | {cell('phone_8k')} | {cell('phone_mulaw')} | {by['clean']['hyp'][:90]} |")

    if own_rows:
        md += ["", "## 5b. Does phone quality change what is heard? (your clips: how different is the phone transcript from the clean one)", "",
               "This needs no ground truth, so it is fair even for clips where you did not read the listed sentence word for word.", "",
               "| Clip | Phone 8 kHz differs from clean by | Phone mu-law differs from clean by |", "|---|---|---|"]
        diffs8, diffsm = [], []
        for cid in dict.fromkeys(r["id"] for r in own_rows):
            by = {r["cond"]: r for r in own_rows if r["id"] == cid}
            if len(by) == 3:
                d8, dm = wer(by["clean"]["hyp"], by["phone_8k"]["hyp"]), wer(by["clean"]["hyp"], by["phone_mulaw"]["hyp"])
                diffs8.append(d8); diffsm.append(dm)
                md.append(f"| {cid} | {pct(d8)} | {pct(dm)} |")
        md.append(f"| **average** | **{pct(mean(diffs8))}** | **{pct(mean(diffsm))}** |")

    num_rows = [r for r in rows if r["numbers_ok"] is not None]
    if num_rows:
        md += ["", "## 6. Numbers heard exactly right?", "", "| Clip | Source | Expected | Clean | Phone 8 kHz | Phone mu-law |", "|---|---|---|---|---|---|"]
        for cid, kind in dict.fromkeys((r["id"], r["kind"]) for r in num_rows):
            by = {r["cond"]: r for r in num_rows if r["id"] == cid and r["kind"] == kind}
            cells = [("OK" if by[c]["numbers_ok"] else "WRONG: heard " + (", ".join(by[c]["heard_numbers"]) or "no number")) if c in by else "-" for c in CONDITIONS]
            md.append(f"| {cid} | {kind} | {', '.join(by['clean']['expected_numbers'])} | " + " | ".join(cells) + " |")
        bad = [r for r in num_rows if not r["numbers_ok"]]
        md += ["", f"**{len(num_rows) - len(bad)} of {len(num_rows)} number checks passed.**" + ("" if not bad else " Mistakes: " + "; ".join(f"{r['id']} ({r['kind']}, {r['cond']}): heard {r['heard_numbers']}" for r in bad))]

    secs = sorted(r["secs"] for r in rows if r["secs"] and r["secs"] > 0)
    if secs:
        md += ["", f"## Speed of one speech-to-text call (not streaming): median {secs[len(secs) // 2]:.1f}s, slowest {secs[-1]:.1f}s ({len(secs)} calls)"]
    failed = [r for r in rows if r["hyp"].startswith("[FAILED")]
    if failed:
        md += ["", f"**{len(failed)} calls failed or hung and count as 100% errors:** " + ", ".join(f"{r['id']}/{r['cond']}" for r in failed)]
    worst = sorted((r for r in rows if r["kind"] != "synth"), key=lambda r: -r["wer_inside"])[:8]
    md += ["", "## Worst 8 real-voice clips (what was said vs what was heard)", "", "| Clip | Condition | WER | Reference | Heard |", "|---|---|---|---|---|"]
    md += [f"| {r['id']} | {r['cond']} | {pct(r['wer'])} | {r['ref'][:70]} | {r['hyp'][:90]} |" for r in worst]
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    OUT_JSON.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    tag = stt_id.replace(":", "-").replace("/", "-") + ("-hint" if hint else "")      # a copy per provider, so runs can be compared
    (OUT_MD.parent / f"speech-bakeoff--{tag}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (OUT_MD.parent / f"speech-bakeoff--{tag}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n" + "\n".join(md))


if __name__ == "__main__":
    main()
