"""Show Sarvam credit use. `python scripts/sarvam_credits.py` prints the total and what was used since the last time you ran it.
Add --peek to look without moving the 'since last time' marker."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
import app.config  # noqa: E402,F401  (loads .env)
from app.speech.credits import CreditLedger  # noqa: E402

led = CreditLedger()
print(led.summary())
print(led.session_line(update="--peek" not in sys.argv))
if led.message():
    print("WARNING:", led.message())
