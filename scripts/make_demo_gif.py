"""Builds docs/demo/practice-call.gif from the REAL logs of the practice calls (docs/results/.phase4-practice-final-english.json).
Nothing is invented: every line on the screen is a line the bot heard or said in a recorded practice run (computer-voice agent, browser path)."""
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
W, H = 760, 420
FONT = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 17)
BOLD = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 21)
SMALL = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 13)
BG, FG, MUTED, AGENT, AI, NOTE = (250, 250, 247), (30, 30, 30), (120, 120, 120), (13, 71, 161), (27, 94, 32), (180, 83, 9)


def wrap(text, font, width, draw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= width:
            cur = t
        else:
            lines.append(cur); cur = w
    return lines + [cur] if cur else lines


def frame(title, subtitle, shown):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((24, 14), title, font=BOLD, fill=FG)
    d.text((24, 44), subtitle, font=SMALL, fill=MUTED)
    d.line((24, 66, W - 24, 66), fill=(220, 220, 215))
    y = 80
    rows = []
    for kind, text in shown:
        label, color = {"agent": ("Agent (computer voice)", AGENT), "ai": ("Nivaran AI", AI), "note": ("", NOTE)}[kind]
        lines = wrap(text, FONT, W - 70, d)
        rows.append((label, color, lines, kind))
    # show only what fits: drop the oldest rows
    def height(r):
        return (24 if r[0] else 0) + 22 * len(r[2]) + 8
    while sum(height(r) for r in rows) > H - 90 and len(rows) > 1:
        rows.pop(0)
    for label, color, lines, kind in rows:
        if label:
            d.text((24, y), label, font=SMALL, fill=color); y += 20
        for ln in lines:
            d.text((38 if label else 24, y), ln, font=FONT, fill=color if kind != "note" else NOTE); y += 22
        y += 8
    d.text((24, H - 26), "Real log of a practice call: browser path, phone-quality sound, no real phone. See docs/results/phase4-practice-results.md", font=SMALL, fill=MUTED)
    return im


def storyboard(call, title, subtitle):
    out, shown = [], []
    ev = [e for e in call["events"] if e["kind"] in ("heard", "spoke") or e["text"].startswith(("pressed keypad", "on hold", "off hold", "call ended"))]
    for e in ev:
        if e["kind"] == "heard":
            shown.append(("agent", e["text"]))
        elif e["kind"] == "spoke":
            shown.append(("ai", e["text"]))
        else:
            txt = {"pressed keypad": "AI pressed key " + e["text"].split(":")[-1].strip(), "on hold": "On hold: the AI waits quietly",
                   "off hold": "A person is talking again", "call ended": "The AI ended the call"}[next(k for k in ("pressed keypad", "on hold", "off hold", "call ended") if e["text"].startswith(k))]
            shown.append(("note", txt))
        out.append((frame(title, subtitle, list(shown)), 1800 if e["kind"] != "note" else 1300))
    out.append((out[-1][0], 2000))
    return out


def main():
    data = {r["n"]: r for r in json.loads((ROOT / "docs" / "results" / ".phase4-practice-final-english.json").read_text())}
    frames = []
    for n, title, sub in ((3, "1. Phone menus: the AI presses the right keys", "Call 3 of the practice series"),
                          (5, "2. Hold music: the AI stays silent", "Call 5"), (6, "3. Asked for an OTP and a card number: it refuses", "Call 6")):
        frames += storyboard(data[n], title, sub)
    out = ROOT / "docs" / "demo" / "practice-call.gif"
    out.parent.mkdir(exist_ok=True)
    imgs = [f for f, _ in frames]
    imgs[0].save(out, save_all=True, append_images=imgs[1:], duration=[d for _, d in frames], loop=0, optimize=True)
    print(out, round(out.stat().st_size / 1024), "KB,", len(imgs), "frames")


if __name__ == "__main__":
    main()
