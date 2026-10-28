"""Builds backend/app/directory/companies.json and docs/results/directory-verification.md from scripts/directory_src.py.

For every source (url, needle[, "browser"]) it re-fetches the official page and looks for a line containing the needle.
 - Found: the whole page line becomes the quote, machine_checked = True.
 - Not found / page blocked: only allowed when the source is marked "browser" (the line was read in a real browser by hand).
   The quote is then the line as given, machine_checked = False.
Also checks that every phone number or email really appears inside its quote.
Usage: python scripts/build_directory.py [--refresh]
"""
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent))
from directory_src import COMPANIES  # noqa: E402
from fetch_text import page_lines  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "scripts" / ".page_cache.json"
OUT_JSON = ROOT / "backend" / "app" / "directory" / "companies.json"
OUT_DOC = ROOT / "docs" / "results" / "directory-verification.md"
TODAY = date.today().isoformat()


def norm(s: str) -> str:
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-")
    return re.sub(r"\s+", " ", s).strip().casefold()


def digits(s: str) -> str:
    return re.sub(r"\D", "", s)


def load_pages(urls: list[str], refresh: bool) -> dict[str, list[str] | None]:
    cache = {} if refresh or not CACHE.exists() else json.loads(CACHE.read_text())
    todo = [u for u in urls if u not in cache]

    def get(u):
        try:
            return u, page_lines(u, timeout=40)
        except Exception:
            return u, None

    with ThreadPoolExecutor(6) as pool:
        for u, lines in pool.map(get, todo):
            cache[u] = lines
    CACHE.write_text(json.dumps(cache, ensure_ascii=False))
    return cache


def make_source(spec, pages) -> dict:
    url, needle, *flag = spec
    lines = pages.get(url)
    found = None
    if lines:
        n = norm(needle)
        for ln in lines:
            if n in norm(ln):
                found = ln
                break
    if found:
        if len(found) > 500:
            i = max(0, norm(found).find(norm(needle)) - 150)
            found = "..." + found[i:i + 500] + "..."
        return {"url": url, "kind": "website", "quote": found, "checked_on": TODAY, "machine_checked": True}
    if "browser" in flag:
        return {"url": url, "kind": "website", "quote": needle, "checked_on": TODAY, "machine_checked": False}
    raise SystemExit(f"NOT FOUND on page and not marked browser: {url}\n  needle: {needle}")


def value_in(value: str, quote: str, kind: str) -> bool:
    if kind == "email":
        return value.lower() in quote.lower()
    return digits(value) in digits(quote)


def main() -> None:
    urls = sorted({s[0] for c in COMPANIES for key in ("phones", "emails") for item in c.get(key, []) for s in item[3 if key == "phones" else 2]}
                  | {s[0] for c in COMPANIES for s in ([c["no_phone"]] if c.get("no_phone") else [])}
                  | {s[0] for c in COMPANIES if c.get("grievance") for s in c["grievance"]["sources"]})
    pages = load_pages(urls, "--refresh" in sys.argv)
    out = []
    for c in COMPANIES:
        helplines, emails = [], []
        for number, label, hours, srcs, *rest in c.get("phones", []):
            role = rest[0] if rest else None
            sources = [make_source(s, pages) for s in srcs]
            for s in sources:
                if not value_in(number, s["quote"], "phone"):
                    raise SystemExit(f"{c['name']}: {number} not inside its quote: {s['quote'][:120]}")
            helplines.append({"kind": "phone", "value": number, "label": label, "hours": hours, "role": role, "sources": sources})
        for value, label, srcs, *rest in c.get("emails", []):
            role = rest[0] if rest else None
            sources = [make_source(s, pages) for s in srcs]
            for s in sources:
                if not value_in(value, s["quote"], "email"):
                    raise SystemExit(f"{c['name']}: {value} not inside its quote: {s['quote'][:120]}")
            emails.append({"kind": "email", "value": value, "label": label, "hours": None, "role": role, "sources": sources})
        g = c.get("grievance")
        grievance = None
        if g:
            grievance = {"name": g.get("name"), "email": g.get("email"), "phone": g.get("phone"), "address": g.get("address"),
                         "sources": [make_source(s, pages) for s in g["sources"]]}
        no_phone = make_source(c["no_phone"], pages) if c.get("no_phone") else None
        out.append({
            "name": c["name"], "aliases": c.get("aliases", []), "category": c["category"],
            "official_domains": c["domains"], "source_url": c["page"], "checked_on": TODAY,
            "helplines": helplines, "emails": emails, "grievance_officer": grievance,
            "working_hours": c.get("hours"), "channel_notes": c.get("notes"),
            "official_no_phone": no_phone, "needs_check": c.get("needs_check", []),
        })
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_doc(out)
    n_ok = sum(s["machine_checked"] for c in out for h in c["helplines"] + c["emails"] for s in h["sources"])
    n_all = sum(len(h["sources"]) for c in out for h in c["helplines"] + c["emails"])
    print(f"{len(out)} companies written. Quotes re-found on the live page by script: {n_ok}/{n_all}")


def write_doc(companies: list[dict]) -> None:
    L = ["# Directory verification checklist", "",
         f"Generated {TODAY} by `scripts/build_directory.py`. For every contact below: open the link, find the exact line, and tick the box.",
         "", "- `machine_checked: yes` = our script re-fetched the page and found that exact line.",
         "- `machine_checked: no` = the page blocked our script; the line was read in a real browser. Check it yourself.",
         "- `two_sources` = the phone number appears on 2 different official pages. `single_source` = only 1.",
         "- Contacts are only ever copied from the company's own official pages. Nothing comes from search results.", ""]
    for c in companies:
        L += [f"## {c['name']} ({c['category']})", f"Main page: {c['source_url']}", ""]
        if c["official_no_phone"]:
            s = c["official_no_phone"]
            L += [f"- [ ] **No customer phone line** (official). {s['url']} (machine_checked: {'yes' if s['machine_checked'] else 'no'})",
                  f"  > {s['quote']}"]
        for h in c["helplines"]:
            conf = "two_sources" if len({s['url'] for s in h['sources']}) >= 2 else "single_source"
            L += [f"- [ ] **Phone {h['value']}** ({h['label']}) `{conf}`"]
            for s in h["sources"]:
                L += [f"  - {s['url']} (machine_checked: {'yes' if s['machine_checked'] else 'no'})", f"    > {s['quote']}"]
        for e in c["emails"]:
            L += [f"- [ ] **Email {e['value']}** ({e['label']})"]
            for s in e["sources"]:
                L += [f"  - {s['url']} (machine_checked: {'yes' if s['machine_checked'] else 'no'})", f"    > {s['quote']}"]
        g = c["grievance_officer"]
        if g:
            L += [f"- [ ] **Grievance officer** {g.get('name') or ''} {g.get('email') or ''}".rstrip()]
            for s in g["sources"]:
                L += [f"  - {s['url']} (machine_checked: {'yes' if s['machine_checked'] else 'no'})", f"    > {s['quote']}"]
        if c["channel_notes"]:
            L += [f"- Notes: {c['channel_notes']}"]
        for n in c["needs_check"]:
            L += [f"- [ ] **NEEDS CHECK (you fill in or drop):** {n}"]
        L += [""]
    OUT_DOC.write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
