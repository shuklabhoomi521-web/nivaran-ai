"""Runs the full problem set against the REAL Claude API. Costs money.

Run only when you choose:  python -m pytest -m paid_api -s
Writes the baseline score table to docs/baseline-phase1.md (+ .json).
"""
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

import pytest

from app.brain.llm import AnthropicLLM
from app.brain.understand import understand
from app.config import get_settings
from app.evaluation import evaluate, load_problems, score_tables

pytestmark = pytest.mark.paid_api
DOCS = Path(__file__).resolve().parents[2] / "docs"
PROBLEMS = load_problems()


@pytest.fixture(scope="module")
def results():
    assert len(PROBLEMS) == 30, (
        f"The final set must have 30 problems; found {len(PROBLEMS)}. "
        "Add the founder's 5 to tests/data/problems_founder5.json first.")
    llm = AnthropicLLM()

    def run(p):
        return evaluate(p, understand(p["message"], llm))

    with ThreadPoolExecutor(max_workers=5) as pool:
        res = list(pool.map(run, PROBLEMS))

    model = get_settings().claude_model
    n_ok = sum(r.correct for r in res)
    n_pass = sum(r.passed for r in res)
    md = [
        "# Phase 1 baseline (understand endpoint)", "",
        f"- Date: {date.today()}", f"- Model: `{model}`",
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
        {"model": model, "date": str(date.today()),
         "results": [{"id": r.id, "language": r.language, "category": r.category,
                      "checks": r.checks, "notes": r.notes} for r in res]},
        indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n" + score_tables(res))
    return {r.id: r for r in res}


@pytest.mark.parametrize("problem", PROBLEMS, ids=[p["id"] for p in PROBLEMS])
def test_problem(problem, results):
    r = results[problem["id"]]
    assert r.passed, f"{r.id}: failed {[k for k, v in r.checks.items() if not v]} {r.notes}"
