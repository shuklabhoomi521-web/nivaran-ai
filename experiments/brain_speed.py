"""Compare how fast each brain answers the SAME spoken turns (one AI call each). Usage: brain_speed.py gemini|groq [model]"""
import os
import sys
import time

sys.path.insert(0, "backend")
from app.config import get_settings  # noqa: E402,F401  (loads .env)
from app.brain.llm import GeminiLLM, GroqLLM  # noqa: E402
from app.brain.understand import understand  # noqa: E402

TURNS = [
    ("english", "My Zomato order came 40 minutes late and the food was cold and I want a refund."),
    ("hinglish", "Order number 4839201 hai, Amazon ne galat size ki kurti bhej di."),
    ("hindi", "मेरा ज़ोमैटो का खाना ठंडा आया, मुझे पैसे वापस चाहिए।"),
    ("tamil", "என் ஸ்விக்கி ஆர்டர் குளிர்ந்து வந்தது. எனக்கு பணம் திரும்ப வேண்டும்."),
]
which = sys.argv[1]
if len(sys.argv) > 2:
    os.environ["GROQ_MODEL" if which == "groq" else "GEMINI_MODEL"] = sys.argv[2]
llm = GroqLLM() if which == "groq" else GeminiLLM()
print(f"== {which} {sys.argv[2] if len(sys.argv) > 2 else '(default model)'}")
for lang, text in TURNS:
    t0 = time.time()
    try:
        r = understand(text, llm, from_speech=True)
        print(f"{lang:9} {time.time()-t0:5.1f}s  {r.case.company}/{r.case.category.value}/{r.case.user_goal.value} | ask={r.follow_up_question!r} | say={r.spoken_reply!r}"[:260])
    except Exception as e:  # noqa: BLE001
        print(f"{lang:9} {time.time()-t0:5.1f}s  ERROR {type(e).__name__} {str(e)[:80]}")
