"""Fetch an official page and print its visible text, one line per block.
Used to copy EXACT lines into the company directory (and to re-check them later).
Usage: python scripts/fetch_text.py URL [--grep word1,word2]"""
import re
import sys

import httpx

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36",
      "Accept-Language": "en-IN,en;q=0.9"}


def page_lines(url: str, timeout: float = 25) -> list[str]:
    r = httpx.get(url, headers=UA, follow_redirects=True, timeout=timeout)
    r.raise_for_status()
    if "pdf" in r.headers.get("content-type", "").lower() or url.lower().split("?")[0].endswith(".pdf"):
        import subprocess
        out = subprocess.run(["pdftotext", "-layout", "-", "-"], input=r.content, capture_output=True).stdout.decode("utf-8", "ignore")
        return [re.sub(r"\s+", " ", ln).strip() for ln in out.split("\n") if ln.strip()]
    html = r.text
    html = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", html)
    html = re.sub(r"(?i)<(br|/p|/div|/li|/tr|/h\d|/td|/section)[^>]*>", "\n", html)
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    text = (text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"')
                .replace("&lt;", "<").replace("&gt;", ">").replace("&#x27;", "'"))
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.split("\n")]
    return [ln for ln in lines if ln]


if __name__ == "__main__":
    url = sys.argv[1]
    words = []
    if "--grep" in sys.argv:
        words = [w.lower() for w in sys.argv[sys.argv.index("--grep") + 1].split(",")]
    try:
        lines = page_lines(url)
    except Exception as e:
        print(f"FETCH FAILED: {type(e).__name__}: {str(e)[:150]}")
        sys.exit(1)
    for ln in lines:
        if not words or any(w in ln.lower() for w in words):
            print(ln[:400])
