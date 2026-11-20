"""List (and optionally act on) cases with no activity for a year.
  python scripts/purge_inactive.py            # dry run: only shows what would happen
  python scripts/purge_inactive.py --warn     # mark cases as warned (the app then shows the 48 hour banner)
  python scripts/purge_inactive.py --delete   # delete cases whose 48 hour warning is over and where nothing happened since
Deleting asks for no extra confirmation, so run the dry run first."""
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.cases.retention import mark_warned, plan  # noqa: E402
from app.cases.store import CaseStore  # noqa: E402

store = CaseStore(os.getenv("CASE_STORE_FILE", "backend/.cases.json"))
today = date.today()
warn, delete = plan(store.list(), today)
print(f"to warn: {[c.id for c in warn]}\nto delete: {[c.id for c in delete]}")
if "--warn" in sys.argv:
    for c in warn:
        store.save(mark_warned(c, today))
    print(f"warned {len(warn)} case(s)")
if "--delete" in sys.argv:
    for c in delete:
        store.delete(c.id)
    print(f"deleted {len(delete)} case(s)")
