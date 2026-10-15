"""Runs the full problem set against the REAL LLM (Gemini free tier by default).

Run only when you choose:  python -m pytest -m live_api -s
- Slows itself down to stay inside the free limits (GEMINI_RPM / GEMINI_RPD in .env).
- Saves each answer in a cache file, so if the daily limit stops the run, running it again
  tomorrow continues where it stopped.
- Writes the baseline score table to docs/baseline-phase1.md (+ .json).
"""
import json
from datetime import date
from pathlib import Path

import pytest

from app.brain.llm import make_llm
from app.brain.ratelimit import DailyQuotaExceeded
from app.brain.understand import understand
from app.config import get_settings
from app.evaluation import evaluate, load_problems, score_tables
from app.models.case import UnderstandResponse

pytestmark = pytest.mark.live_api
DOCS = Path(__file__).resolve().parents[2] / "docs"
PROBLEMS = load_problems()


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

    res = []
    for i, p in enumerate(PROBLEMS, 1):
        if p["id"] in cache:
            resp = UnderstandResponse.model_validate(cache[p["id"]])
        else:
            try:
                resp = understand(p["message"], llm)
            except DailyQuotaExceeded as e:
                cache_file.write_text(json.dumps(cache, ensure_ascii=False))
                pytest.fail(f"{e} {len(cache)} of {len(PROBLEMS)} done and saved. Run again later to continue.")
            cache[p["id"]] = resp.model_dump(mode="json")
            cache_file.write_text(json.dumps(cache, ensure_ascii=False))
            print(f"  [{i}/{len(PROBLEMS)}] {p['id']} done")
        res.append(evaluate(p, resp))

    n_ok = sum(r.correct for r in res)
    n_pass = sum(r.passed for r in res)
    md = [
        "# Phase 1 baseline (understand endpoint)", "",
        f"- Date: {date.today()}", f"- Provider: `{provider}`; model: `{model}`",
        f"- Problems: {len(res)}; correct (company, category, goal, no invented facts): {n_ok}; "
        f"fully passed (plus safety and asking checks): {n_pass}", "",
        score_tables(res), "", "### Failures", "",
    ]
    fails = [r for r in res if not r.passed]
    md += [f"- `{r.id}`: " + ", ".join(k for k, v in r.checks.items() if not v)
           + ((" | " + "; ".join(r.notes)) if r.notes else "") for r in fails] or ["- none"]
    DOCS.mkdir(exist_ok=True)
    (DOCS / "baseline-phase1.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (DOCS / "baseline-phase1.json").write_text(json.dumps(
        {"provider": provider, "model": model, "date": str(date.today()),
         "results": [{"id": r.id, "language": r.language, "category": r.category,
                      "checks": r.checks, "notes": r.notes} for r in res]},
        indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n" + score_tables(res))
    return {r.id: r for r in res}


@pytest.mark.parametrize("problem", PROBLEMS, ids=[p["id"] for p in PROBLEMS])
def test_problem(problem, results):
    r = results[problem["id"]]
    assert r.passed, f"{r.id}: failed {[k for k, v in r.checks.items() if not v]} {r.notes}"
