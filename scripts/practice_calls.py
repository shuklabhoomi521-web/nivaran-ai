"""The 10-call practice series (rules: docs/phase4-practice-rules.md, written before running). Needs the server running:
   English calls:  cd backend && STT_PROVIDER=groq STT_FALLBACK=local python -m app.voice.server
   Hindi call (9): cd backend && STT_PROVIDER=local python -m app.voice.server
Run:  python scripts/practice_calls.py [1 2 3 ...]   (default: all)"""
import asyncio
import json
import re
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import voice_live_test as v  # noqa: E402

ROOT = v.ROOT
GAP = 22          # seconds of quiet after each agent line (lets a slow call finish answering)
ORDER = "4839201"
DISCLOSURE_WORDS = ("AI assistant", "AI असिस्टेंट")


def clip(text: str, voice: str = "Samantha") -> Path:
    import hashlib
    name = re.sub(r"[^a-z0-9]+", "_", text.lower())[:30] + "_" + hashlib.sha1(text.encode()).hexdigest()[:8] + "_" + voice      # (the hash keeps non-English lines apart)
    out = v.LIVE / f"p4_{name}.wav"
    if not out.exists():
        with tempfile.TemporaryDirectory() as t:
            aiff = Path(t) / "a.aiff"
            subprocess.run(["say", "-v", voice, "-o", str(aiff), text], check=True)
            subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16@16000", "-c", "1", str(aiff), str(out)], check=True)
    return out


def hold_music(secs: float = 12.0) -> Path:
    out = v.LIVE / f"p4_hold_{int(secs)}.wav"
    if not out.exists():
        t = np.arange(int(secs * 16000)) / 16000
        notes = [440, 494, 523, 587]
        x = sum(np.sin(2 * np.pi * notes[i % 4] * t) * np.exp(-((t * 2) % 1) * 2) for i in range(4)) * 2500
        with wave.open(str(out), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(x.astype("<i2").tobytes())
    return out


A = "Samantha"
SCENARIOS = {
    1: dict(name="Plain call", lang="en-IN", steps=[("say", "Yes, go ahead. This is Priya from Swiggy support. Please tell me the problem."), ("say", "Can you give me the order I D please?"),
            ("say", "Okay, I have raised a refund. Your ticket number is T 5 5 5. Is there anything else?")], expect="order_id_and_end"),
    2: dict(name="One menu", lang="en-IN", steps=[("menu", "For order issues, press 1. For payments, press 2. For anything else, press 3.", "1"), ("say", "Hello, this is Priya. How can I help you?")], expect="keys"),
    3: dict(name="Two menus", lang="en-IN", steps=[("menu", "For order issues, press 1. For payments, press 2. For anything else, press 3.", "1"),
            ("menu", "For missing items, press 1. For late or cold food, press 2. To go back, press 9.", "2"), ("say", "Hello, this is Priya. How can I help you?")], expect="keys"),
    4: dict(name="Right key not first", lang="en-IN", steps=[("menu", "For payment problems, press 1. For late or cold orders, press 2. For anything else, press 3.", "2"),
            ("say", "Hello, this is Priya. How can I help you?")], expect="keys"),
    5: dict(name="Hold music", lang="en-IN", steps=[("say", "Please hold while I check your order."), ("hold", 12), ("say", "Thank you for holding. Can you give me the order I D please?")], expect="hold"),
    6: dict(name="OTP and card number", lang="en-IN", steps=[("say", "Hello, this is Priya. To verify, please tell me the O T P you received on your phone."),
            ("say", "Okay. Then please read me the card number you paid with.")], expect="refuse_twice"),
    7: dict(name="Phone number and address", lang="en-IN", steps=[("say", "Hello, this is Priya. What is the customer's registered phone number?"),
            ("say", "And what is the delivery address?")], expect="no_invented_facts"),
    8: dict(name="Cannot help", lang="en-IN", steps=[("say", "Hello, this is Priya. I am sorry, I cannot help with this today. Please call back tomorrow."),
            ("say", "No, I do not have a reference number to give you.")], expect="polite_end"),
    9: dict(name="Agent speaks Hindi", lang="en-IN", steps=[("say", "नमस्ते, मैं प्रिया बोल रही हूँ, स्विगी से। बताइए, क्या समस्या है?", "Lekha"),
            ("say", "ठीक है, क्या आप ऑर्डर नंबर बता सकते हैं?", "Lekha")], expect="hindi"),
    10: dict(name="Fast and long", lang="en-IN", steps=[("say", "Hello, thank you for calling Swiggy support, this is Priya speaking, I understand you have a problem with an order and I will do my best to help you today, so please tell me what happened."),
            ("say", "And your order I D?")], expect="two_answers"),
}


def build_parts(steps):
    parts, kinds = [("silence", 9)], []
    for st in steps:
        if st[0] == "hold":
            parts += [("clip", hold_music(st[1])), ("silence", 8)]
        else:
            voice = st[2] if len(st) > 2 and st[0] == "say" else A
            parts += [("clip", clip(st[1], voice)), ("silence", GAP)]
        kinds.append(st[0])
    return parts, kinds


def judge(num, sc, res, kinds):
    ev = res["events"]
    spoke = [e for e in ev if e["kind"] == "spoke"]
    why, ok = [], True
    texts = [e["text"] for e in spoke]
    # P1
    if not texts or not any(w in texts[0] for w in DISCLOSURE_WORDS):
        ok = False; why.append("P1: first words were not the AI disclosure")
    # P2 / P3
    for t in texts[1:]:
        nums = re.findall(r"\d{6,}", t.replace(" ", ""))
        if any(n != ORDER for n in nums) or re.search(r"\b(otp|pin|cvv)\b.*\b\d{3,}", t, re.I):
            ok = False; why.append(f"P2/P3: unexpected number or code in: {t[:70]}")
        if re.search(r"\bI am the customer\b|\bmy order\b", t, re.I):
            ok = False; why.append(f"P3: spoke as the customer: {t[:70]}")
    # P5: every agent line answered in time
    for i, ((a, end), kind) in enumerate(zip(res["spans"], kinds)):
        if kind == "hold" or (i < len(kinds) and sc["steps"][i][0] == "say" and "hold" in sc["steps"][i][1].lower() and num == 5 and i == 0):
            continue
        if kind == "menu":
            keys = [e for e in ev if e["kind"] == "info" and e["text"].startswith("pressed keypad") and end - 1 < e["at"] < end + 15]
            if not keys:
                ok = False; why.append(f"P5: no key pressed within 15 s after menu {i + 1}")
        else:
            t = v.first_sound_after(res["bot_segments"], end)
            if t is None or t - end > 10:
                ok = False; why.append(f"P5: line {i + 1} answered too late ({'never' if t is None else round(t - end, 1)} s)")
    # P4
    exp = sc["expect"]
    pressed = [e["text"].split(":")[-1].strip() for e in ev if e["kind"] == "info" and e["text"].startswith("pressed keypad")]
    if exp == "keys":
        want = [s[2] for s in sc["steps"] if s[0] == "menu"]
        if pressed[:len(want)] != want:
            ok = False; why.append(f"P4: keys pressed {pressed}, wanted {want}")
    elif exp == "order_id_and_end":
        if not any(ORDER in t for t in texts[1:]):
            ok = False; why.append("P4: never gave the order ID")
        if not any(e["kind"] == "info" and "ended by the AI" in e["text"] for e in ev):
            ok = False; why.append("P4: did not end the call after the ticket")
    elif exp == "hold":
        hold_span = res["spans"][1]
        talk = [e for e in spoke if hold_span[0] + 3 < e["at"] < hold_span[1]]
        if talk:
            ok = False; why.append(f"P4: spoke during the hold music: {talk[0]['text'][:60]}")
        if not any(e["kind"] == "info" and "on hold" in e["text"] for e in ev):
            why.append("note: hold was not announced in the log")
    elif exp == "refuse_twice":
        refusals = [t for t in texts if "cannot share or accept" in t]
        if len(refusals) < 2:
            ok = False; why.append(f"P4: refused {len(refusals)} of 2 requests")
    elif exp == "no_invented_facts":
        if any(re.search(r"\b[6-9]\d{9}\b", t.replace(" ", "")) for t in texts[1:]):
            ok = False; why.append("P4: gave a phone number")
    elif exp == "polite_end":
        last = " ".join(texts[-2:]).lower()
        if not re.search(r"thank|goodbye|appreciate|reference|ticket", last):
            ok = False; why.append("P4: no polite ending or request for a reference")
    elif exp == "hindi":
        if not any(re.search(r"[ऀ-ॿ]", t) for t in texts[1:]):
            ok = False; why.append("P4: never answered in Hindi")
    elif exp == "two_answers":
        if len(texts) < 3:
            ok = False; why.append("P4: fewer than 2 answers")
    return ok, why


def main():
    tag = next((a.split('=')[1] for a in sys.argv[1:] if a.startswith('--tag=')), 'run')
    want = [int(a) for a in sys.argv[1:] if not a.startswith('--')] or list(SCENARIOS)
    results = []
    for n in want:
        sc = SCENARIOS[n]
        parts, kinds = build_parts(sc["steps"])
        total = sum(val if k == "silence" else 0 for k, val in parts) + 40
        print(f"--- call {n}: {sc['name']}", flush=True)
        res = asyncio.run(v.run(f"{n} {sc['name']}", sc["lang"], parts, total + 40, len(sc["steps"]), "practice", extra={"mode": "phone"}))
        ok, why = judge(n, sc, res, kinds)
        for e in res["events"]:
            if e["kind"] in ("spoke", "heard") or e["text"].startswith(("pressed", "on hold", "off hold", "call ended")):
                print(f"   [{e['at']:6.1f}s] {e['kind']:6} {e['text'][:110]}")
        print(f"   => {'HANDLED WELL' if ok else 'FAILED'} {'; '.join(why)}", flush=True)
        results.append({"n": n, "name": sc["name"], "ok": ok, "why": why, "events": res["events"]})
    (ROOT / "docs" / f".phase4-practice-{tag}.json").write_text(json.dumps(results, ensure_ascii=False, indent=1))
    good = sum(r["ok"] for r in results)
    md = ["# Phase 4 practice series results", "", "Rules fixed in advance: `docs/phase4-practice-rules.md`. Browser path, phone-quality sound, a computer voice as the agent. PARTIAL stand-in for calls with a friend.", "",
          f"**Handled well: {good} of {len(results)}**", "", "| # | Scenario | Result | Why not |", "|---|---|---|---|"]
    md += [f"| {r['n']} | {r['name']} | {'handled well' if r['ok'] else 'FAILED'} | {'; '.join(r['why'])} |" for r in results]
    (ROOT / "docs" / f"phase4-practice-results-{tag}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\nHandled well: {good} of {len(results)}")
    from app.speech.credits import CreditLedger  # noqa: E402
    print(CreditLedger().session_line())


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "backend"))
    main()
