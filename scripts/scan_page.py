"""Print only the lines of an official page that contain a phone number, an email or a grievance word."""
import re
import sys

sys.path.insert(0, "scripts")
from fetch_text import page_lines  # noqa: E402

PHONE = re.compile(r"(?<!\d)(1800[\s-]?\d[\d\s-]{5,10}|1860[\s-]?\d[\d\s-]{5,10}|\+?91[\s-]?\d{5}[\s-]?\d{5}|0\d{2,4}[\s-]?\d{6,8}|\d{5}[\s-]?\d{5}|\b1\d{2,4}\b)(?!\d)")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")
WORDS = ("grievance", "nodal", "helpline", "toll", "customer care", "call us", "contact us", "ombudsman")

for url in sys.argv[1:]:
    print(f"=== {url}")
    try:
        lines = page_lines(url, timeout=45)
    except Exception as e:
        print(f"   FETCH FAILED: {type(e).__name__} {str(e)[:80]}")
        continue
    shown = 0
    for ln in lines:
        low = ln.lower()
        if EMAIL.search(ln) or (PHONE.search(ln) and any(w in low for w in ("call", "toll", "phone", "helpline", "care", "contact", "number", "dial"))) or any(w in low for w in WORDS):
            print("   " + ln[:230])
            shown += 1
            if shown >= 14:
                break
    if shown == 0:
        print("   (nothing useful found: page may be built by JavaScript)")
