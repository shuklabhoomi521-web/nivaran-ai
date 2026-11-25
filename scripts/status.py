"""Builds docs/STATUS.md and docs/STATUS.html from docs/status/status.json (the live project tracker).
Edit the JSON, run `python3 scripts/status.py`, open docs/STATUS.html and refresh."""
import html, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "docs/status/status.json").read_text(encoding="utf-8"))
LABEL = {"done": "Done", "doing": "In progress", "next": "Planned next", "you": "Needs you", "waiting": "Waiting", "blocked": "Blocked"}
COLOR = {"done": "#2F6F8F", "doing": "#1F4E8C", "next": "#6B7280", "you": "#A5546B", "waiting": "#8A6A4A", "blocked": "#7A2E2E"}
items = [i for g in data["groups"] for i in g["items"]]
count = {k: sum(1 for i in items if i["s"] == k) for k in LABEL}
pct = round(100 * count["done"] / len(items))

md = [f"# Nivaran project tracker\n\nUpdated {data['updated']}. {data['headline']}\n", f"**{count['done']} of {len(items)} items done ({pct}%).** " + " · ".join(f"{LABEL[k]}: {count[k]}" for k in LABEL if k != "done") + "\n"]
for g in data["groups"]:
    md.append(f"\n## {g['name']}\n\n| Status | Item | Detail |\n|---|---|---|")
    md += [f"| {LABEL[i['s']]} | {i['t']} | {i['d']} |" for i in g["items"]]
(ROOT / "docs/STATUS.md").write_text("\n".join(md) + "\n", encoding="utf-8")

e = html.escape
rows = ""
for g in data["groups"]:
    rows += f"<h2>{e(g['name'])}</h2><div class=card>"
    for i in g["items"]:
        rows += f"<div class=row><span class=b style='color:{COLOR[i['s']]};border-color:{COLOR[i['s']]}'>{LABEL[i['s']]}</span><div><b>{e(i['t'])}</b><div class=d>{e(i['d'])}</div></div></div>"
    rows += "</div>"
chips = "".join(f"<span class=chip style='border-top-color:{COLOR[k]}'><b>{count[k]}</b> {LABEL[k]}</span>" for k in LABEL)
page = f"""<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Nivaran project tracker</title>
<style>body{{font-family:Inter,'Segoe UI',system-ui,sans-serif;background:#F3F5F8;color:#172033;margin:0}}header{{background:#14253F;color:#fff;padding:22px 20px}}
main{{max-width:900px;margin:0 auto;padding:16px 20px 40px}}h1{{margin:0;font-size:22px}}h2{{font-size:16px;margin:26px 0 8px}}.sub{{color:#C9D3E3;font-size:13px;margin-top:6px}}
.bar{{height:8px;background:#D8DEE8;border-radius:4px;margin:14px 0}}.bar i{{display:block;height:8px;background:#1F4E8C;border-radius:4px;width:{pct}%}}
.chips{{display:flex;flex-wrap:wrap;gap:8px}}.chip{{background:#fff;border:1px solid #D8DEE8;border-top:3px solid;border-radius:8px;padding:8px 12px;font-size:13px}}.chip b{{font-size:18px;margin-right:4px}}
.card{{background:#fff;border:1px solid #D8DEE8;border-radius:10px;box-shadow:0 1px 2px rgba(16,24,40,.06)}}.row{{display:flex;gap:12px;padding:12px 14px;border-bottom:1px solid #E8ECF2}}.row:last-child{{border:0}}
.b{{flex:none;align-self:flex-start;font-size:11.5px;font-weight:600;border:1px solid;border-radius:6px;padding:2px 8px;min-width:78px;text-align:center}}.d{{color:#5A6577;font-size:13px;margin-top:2px}}</style>
<header><h1>Nivaran project tracker</h1><div class=sub>Updated {e(data['updated'])} · {e(data['headline'])}</div></header>
<main><div class=bar><i></i></div><p><b>{count['done']} of {len(items)} items done ({pct}%)</b></p><div class=chips>{chips}</div>{rows}</main>"""
(ROOT / "docs/STATUS.html").write_text(page, encoding="utf-8")
print(f"{count['done']}/{len(items)} done ({pct}%)", {LABEL[k]: v for k, v in count.items()})
