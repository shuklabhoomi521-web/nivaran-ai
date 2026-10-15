"""Re-score saved answers (no API calls). Usage: python scripts/rescore_from_cache.py"""
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.config import get_settings  # noqa: E402
from app.evaluation import baseline_markdown, load_problems  # noqa: E402
from app.models.case import UnderstandResponse  # noqa: E402

s = get_settings()
model = s.gemini_model if s.provider == "gemini" else s.claude_model
cache = json.loads((ROOT / "docs" / f".live-cache-{s.provider}-{model}.json").read_text())
problems = load_problems()
responses = {p["id"]: UnderstandResponse.model_validate(cache[p["id"]]) for p in problems}
meta = {"date": str(date.today()), "provider": s.provider, "model": model}
md, strict, meaning = baseline_markdown(problems, responses, meta)
(ROOT / "docs" / "baseline-phase1.md").write_text(md, encoding="utf-8")
(ROOT / "docs" / "baseline-phase1.json").write_text(json.dumps(
    {**meta, "results_meaning_based": [r.__dict__ for r in meaning], "results_strict": [r.__dict__ for r in strict]},
    indent=2, ensure_ascii=False), encoding="utf-8")
print(md)
