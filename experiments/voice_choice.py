"""Voice-choice step: the same reply read by Sarvam's voice and Gemini's voice, in 4 languages, so you can listen and pick.
Uses Sarvam credits on purpose (allowed for this step): about Rs 2 for everything. Output: speech_test/voice_choice/ + a listening page."""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
import app.config  # noqa: E402,F401
from app.speech.credits import CreditLedger  # noqa: E402
from app.speech.gemini import GeminiTTS  # noqa: E402
from app.speech.sarvam import SarvamTTS  # noqa: E402

OUT = ROOT / "speech_test" / "voice_choice"
OUT.mkdir(parents=True, exist_ok=True)
SENTENCES = {
    "English": ("en-IN", "I understood: your Swiggy order arrived cold and you want a refund. Swiggy has no phone line, so I would send a complaint email. Nothing has been sent yet."),
    "Hindi": ("hi-IN", "मैं समझ गया: आपका Swiggy का ऑर्डर ठंडा आया और आप रिफंड चाहते हैं। Swiggy की कोई फ़ोन लाइन नहीं है, इसलिए मैं शिकायत का ईमेल लिखूँगा। अभी कुछ भेजा नहीं गया है।"),
    "Tamil": ("ta-IN", "புரிந்துகொண்டேன்: உங்கள் Swiggy ஆர்டர் குளிர்ந்து வந்தது, உங்களுக்கு பணம் திரும்ப வேண்டும். Swiggy-க்கு தொலைபேசி எண் இல்லை, அதனால் நான் புகார் மின்னஞ்சல் அனுப்புவேன். இன்னும் எதுவும் அனுப்பப்படவில்லை."),
    "Hinglish": ("hi-IN", "Maine samjha: aapka Swiggy order thanda aaya aur aapko refund chahiye. Swiggy ki koi phone line nahi hai, isliye main complaint email likhunga. Abhi kuch bheja nahi gaya hai."),
}
SARVAM_VOICES = {"English": "simran_en_customer", "Hindi": "ritu_hi_customer", "Tamil": "gokul_ta_narration", "Hinglish": "ishita_enhi_customer"}
rows = []
sarvam, gemini = SarvamTTS(), GeminiTTS()
for lang, (loc, text) in SENTENCES.items():
    for name, fn in (("Sarvam", lambda: sarvam.synthesize(text, loc, voice=SARVAM_VOICES[lang])), ("Gemini", lambda: gemini.synthesize(text, loc))):
        f = OUT / f"{lang.lower()}-{name.lower()}.wav"
        t0 = time.time()
        try:
            a = fn()
            f.write_bytes(a.data)
            secs, err = round(time.time() - t0, 1), None
        except Exception as e:  # noqa: BLE001
            secs, err = round(time.time() - t0, 1), str(e)[:100]
        rows.append({"lang": lang, "provider": name, "file": f.name if not err else None, "secs": secs, "error": err, "chars": len(text),
                     "voice": SARVAM_VOICES[lang] if name == "Sarvam" else "Kore"})
        print(f"{lang:9} {name:7} {secs:5}s  {err or 'ok'}", flush=True)
html = ["<!doctype html><meta charset=utf-8><title>Voice choice</title><style>body{font-family:system-ui;max-width:820px;margin:2rem auto;font-size:18px}td{padding:.4rem .8rem}.box{background:#eef6ff;padding:1rem;border-radius:8px}label{margin-right:1rem}</style>",
        "<h1>Voice choice</h1><div class=box><b>What this page is for.</b> The bot will speak to users in this voice, so we must pick the voice that sounds best. "
        "Below are 4 languages. Each has two voices reading the SAME sentence: <b>Sarvam</b> (paid after free credit, faster) and <b>Gemini</b> (free, slower).<br><br>"
        "<b>What to do:</b> press play on both voices in each language and decide which one is clearer and more natural to your ear. "
        "A voice is bad if it mispronounces words, sounds robotic or is hard to follow. Tick your pick under each language. "
        "At the end press <i>Show my picks</i> and send me that line in chat. There are no wrong answers.</div><table>"]
for lang in SENTENCES:
    html.append(f"<tr><td colspan=3><h2>{lang}</h2><small>{SENTENCES[lang][1]}</small><br>"
                f"<label><input type=radio name={lang} value=Sarvam> Sarvam is better</label><label><input type=radio name={lang} value=Gemini> Gemini is better</label>"
                f"<label><input type=radio name={lang} value=Both> both fine</label><label><input type=radio name={lang} value=Neither> neither is good</label></td></tr>")
    for r in rows:
        if r["lang"] == lang:
            html.append(f"<tr><td>{r['provider']} ({r['voice']})</td><td>{'<audio controls src=\"' + r['file'] + '\"></audio>' if r['file'] else 'FAILED: ' + str(r['error'])}</td><td>made in {r['secs']} s</td></tr>")
html.append("</table><p><button onclick=\"show()\" style='font-size:18px;padding:.5rem 1rem'>Show my picks</button></p><pre id=out style='background:#f4f4f4;padding:1rem'></pre>"
            "<script>function show(){const l=['English','Hindi','Tamil','Hinglish'];document.getElementById('out').textContent='My voice picks: '+l.map(x=>{const c=document.querySelector('input[name='+x+']:checked');return x+': '+(c?c.value:'not chosen')}).join(', ')}</script>")
(OUT / "index.html").write_text("\n".join(html), encoding="utf-8")
(OUT / "results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
print(CreditLedger().session_line())
