"""Runs the full problem set against the REAL LLM (Gemini free tier by default).

Run only when you choose:  python -m pytest -m live_api -s
- Slows itself down to stay inside the free limits (GEMINI_RPM / GEMINI_RPD in .env).
- Saves each answer in a cache file, so if the daily limit stops the run, running it again
  tomorrow continues where it stopped.
- Writes the baseline score table to docs/baseline-phase1.md (+ .json).
"""
import json
import os
from datetime import date
from pathlib import Path

import pytest

from app.brain.llm import make_llm
from app.brain.ratelimit import DailyQuotaExceeded
from app.brain.understand import understand
from app.config import get_settings
from app.evaluation import baseline_markdown, load_problems
from app.models.case import UnderstandResponse

pytestmark = pytest.mark.live_api
DOCS = Path(__file__).resolve().parents[2] / "docs"
PROBLEMS = load_problems()
RERUN_IDS = set(filter(None, os.getenv("RERUN_IDS", "").split(",")))  # e.g. RERUN_IDS=f-04


def _model_name() -> str:
    s = get_settings()
    return s.gemini_model if s.provider == "gemini" else s.claude_model


@pytest.fixture(scope="module")
def results():
    assert len(PROBLEMS) == 30, (
        f"The final set must have 30 problems; found {len(PROBLEMS)}. "
        "Add the founder's 5 to tests/data/problems_founder5.json first.")
    provider, model = get_settings().provider, _model_name()
    cache_file = DOCS / f".live-cache-{provider}-{model}.json"
    cache = json.loads(cache_file.read_text()) if cache_file.exists() else {}
    llm = make_llm()

    responses, stale = {}, []  # stale = answers saved before category_confidence existed: carried over, NOT re-run
    for i, p in enumerate(PROBLEMS, 1):
        if p["id"] in cache and "category_confidence" not in cache[p["id"]]["case"] and p["id"] in RERUN_IDS:
            del cache[p["id"]]
        if p["id"] in cache:
            if "category_confidence" not in cache[p["id"]]["case"]:
                cache[p["id"]]["case"]["category_confidence"] = "high"
                stale.append(p["id"])
            responses[p["id"]] = UnderstandResponse.model_validate(cache[p["id"]])
        else:
            try:
                resp = understand(p["message"], llm)
            except DailyQuotaExceeded as e:
                cache_file.write_text(json.dumps(cache, ensure_ascii=False))
                pytest.fail(f"{e} {len(cache)} of {len(PROBLEMS)} done and saved. Run again later to continue.")
            cache[p["id"]] = resp.model_dump(mode="json")
            cache_file.write_text(json.dumps(cache, ensure_ascii=False))
            responses[p["id"]] = resp
            print(f"  [{i}/{len(PROBLEMS)}] {p['id']} done")

    meta = {"date": str(date.today()), "provider": provider, "model": model}
    md, strict, meaning = baseline_markdown(PROBLEMS, responses, meta, stale)
    DOCS.mkdir(exist_ok=True)
    (DOCS / "baseline-phase1.md").write_text(md, encoding="utf-8")
    (DOCS / "baseline-phase1.json").write_text(json.dumps(
        {**meta, "results_meaning_based": [r.__dict__ for r in meaning], "results_strict": [r.__dict__ for r in strict]},
        indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n" + md)
    return {r.id: r for r in meaning}


@pytest.mark.parametrize("problem", PROBLEMS, ids=[p["id"] for p in PROBLEMS])
def test_problem(problem, results):
    r = results[problem["id"]]
    assert r.passed, f"{r.id}: failed {[k for k, v in r.checks.items() if not v]} {r.notes}"
