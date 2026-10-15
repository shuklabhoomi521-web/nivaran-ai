"""Step 7: for each of the 30 problems, take the AI's saved understand answer (no API calls), look the company up in the
directory and show which official contact we would use. Writes docs/phase2-contact-check.md."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.config import get_settings  # noqa: E402
from app.directory.lookup import find_company  # noqa: E402
from app.directory.picker import pick_contact  # noqa: E402
from app.evaluation import load_problems  # noqa: E402

s = get_settings()
model = s.gemini_model if s.provider == "gemini" else s.claude_model
cache = json.loads((ROOT / "docs" / f".live-cache-{s.provider}-{model}.json").read_text())
rows, ok, with_contact, asked = [], 0, 0, 0
for p in load_problems():
    case = cache[p["id"]]["case"]
    ai_company = case["company"]
    exp = p["expected"]["company"]
    if exp is None:
        good = ai_company is None
        asked += good
        rows.append((p["id"], "(none)", ai_company or "(none)", "-", "-", "OK: no company, so the AI asks a question and no contact is used" if good else "WRONG: AI named a company"))
        ok += good
        continue
    entry = find_company(ai_company)
    exp_entry = find_company(exp) or next((find_company(a) for a in p["expected"].get("company_aliases", []) if find_company(a)), None)
    right = entry is not None and entry is exp_entry
    ch = pick_contact(entry) if entry else None
    chans = ", ".join(c.value for c in ch.channels_available) if ch else "-"
    pick = "-"
    if ch:
        bits = [x for x in ((ch.phone and f"call {ch.phone.value}"), (ch.support_email and f"email {ch.support_email.value}"),
                            (ch.grievance_email and f"complaint {ch.grievance_email.value}")) if x]
        pick = "; ".join(bits) or ("no verified contact yet (needs_check)")
    with_contact += bool(ch and ch.channels_available)
    ok += right
    rows.append((p["id"], exp, ai_company or "(none)", chans or "none", pick, "OK" if right else "WRONG company match"))
md = ["# Phase 2: contact check on the 30 problems", "",
      "Uses the AI's saved answers from the real Phase 1 run (no new API calls). Contacts come only from the verified directory.", "",
      f"- Right company matched in the directory (or correctly no company): **{ok}/30**",
      f"- Problems with a named company that also have at least one verified contact: **{with_contact}/{sum(1 for p in load_problems() if p['expected']['company'])}**",
      f"- Problems with no company that were correctly left for a question: **{asked}**", "",
      "| Problem | Expected company | AI company | Channels available | Contact we would use | Result |", "|---|---|---|---|---|---|"]
md += [f"| {a} | {b} | {c} | {d} | {e} | {f} |" for a, b, c, d, e, f in rows]
(ROOT / "docs" / "phase2-contact-check.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
