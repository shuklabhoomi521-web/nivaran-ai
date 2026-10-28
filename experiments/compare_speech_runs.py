"""Side-by-side table of two bake-off runs (reads the per-provider JSON copies; no API calls).
Usage: python experiments/compare_speech_runs.py <tagA> <tagB>   e.g. gemini_prompt-gemini-3.5-flash-lite-hint sarvam-saaras-v3-hinglish=codemix-hint"""
import json
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1] / "docs" / "results"
a_tag, b_tag = sys.argv[1], sys.argv[2]
A = json.loads((DOCS / f"speech-bakeoff--{a_tag}.json").read_text())
B = json.loads((DOCS / f"speech-bakeoff--{b_tag}.json").read_text())
CONDS = ("clean", "phone_8k", "phone_mulaw")
LABELS = [("hinglish", "own", "Hinglish (your recordings)"), ("english", "own", "Indian English (your recordings)"),
          ("hindi", "public", "Hindi (FLEURS)"), ("tamil", "public", "Tamil (FLEURS)"), ("english", "public", "US English (FLEURS)")]


def avg(rows, lang, kind, noisy, cond, key):
    xs = [r[key] for r in rows if r["lang"] == lang and r["kind"] == kind and r["noisy"] == noisy and r["cond"] == cond]
    return sum(xs) / len(xs) if xs else None


def f(x):
    return "-" if x is None else f"{x:.0%}"


def block(title, noisy):
    out = [f"### {title}", "", f"| Voices | Clean (A / B) | Phone 8 kHz (A / B) | Phone mu-law (A / B) |", "|---|---|---|---|"]
    for lang, kind, label in LABELS:
        key = "wer_inside" if kind == "own" else "wer"
        if avg(A, lang, kind, noisy, "clean", key) is None:
            continue
        out.append(f"| {label} | " + " | ".join(f"{f(avg(A, lang, kind, noisy, c, key))} / {f(avg(B, lang, kind, noisy, c, key))}" for c in CONDS) + " |")
    return out


def numbers(rows):
    n = [r for r in rows if r["numbers_ok"] is not None]
    return sum(r["numbers_ok"] for r in n), len(n)


md = [f"# Speech-to-text comparison: A = `{a_tag}`, B = `{b_tag}`", "",
      "Word error rate (lower is better). Own clips use 'sentence inside' (extra words you spoke are ignored). Same clips, same language hint.", ""]
md += block("Real voices, quiet clips", False) + [""] + block("Real voices, noisy clips", True)
md += ["", "### Computer voices (round trip)", "", "| Language | Clean (A / B) | Phone 8 kHz (A / B) | Phone mu-law (A / B) |", "|---|---|---|---|"]
for lang in ("hinglish", "english", "hindi", "tamil"):
    md.append(f"| {lang} | " + " | ".join(f"{f(avg(A, lang, 'synth', False, c, 'wer'))} / {f(avg(B, lang, 'synth', False, c, 'wer'))}" for c in CONDS) + " |")
md += ["", "> **Caution:** Sarvam's settings were tuned on these same clips (model v3 -> v4, Hinglish mode, company-name key terms), "
        "Gemini's were only adjusted for the language hint. Sarvam's numbers here are therefore optimistic until the new-clips test "
        "(docs/results/speech-settings-frozen.md)."]
na, nb = numbers(A), numbers(B)
md += ["", f"### Numbers heard exactly right (4839201, 299, 1500, 2000, 40): A {na[0]} of {na[1]}, B {nb[0]} of {nb[1]}"]
for tag, rows in (("A", A), ("B", B)):
    bad = [r for r in rows if r["numbers_ok"] is False]
    if bad:
        md += [f"- {tag} mistakes: " + "; ".join(f"{r['id']} {r['kind']} {r['cond']} (heard {r['heard_numbers'] or 'no number'})" for r in bad[:12])]
md += ["", "### Time for one call, measured separately without our slow-down (5 different 5-8 s phone-quality clips)", "",
       "Measured on 2026-10-19: Sarvam median 0.3 s (slowest 1.4 s); Gemini lite model median 5.1 s (slowest 8.5 s). Other timings in the run tables include our own wait between calls and are not real call times."]
(DOCS / "results" / "speech-compare.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
