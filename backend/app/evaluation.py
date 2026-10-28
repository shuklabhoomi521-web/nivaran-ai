"""Scoring for the test set. Reused later as the Phase 9 baseline."""
import difflib
import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from app.models.case import UnderstandResponse
from app.safety.redact import redact

DATA_DIR = Path(__file__).resolve().parent.parent / "tests" / "data"


def load_problems() -> list[dict]:
    problems: list[dict] = []
    for name in ("problems_core25.json", "problems_founder5.json"):
        problems += json.loads((DATA_DIR / name).read_text(encoding="utf-8"))
    return problems


def _norm(s: str) -> str:
    return re.sub(r"[\W_]+", "", s.casefold())


def _company_ok(expected: str | None, aliases: list[str], got: str | None) -> bool:
    if expected is None:
        return got is None
    if got is None:
        return False
    g = _norm(got)
    return any(_norm(a) and (_norm(a) in g or g in _norm(a)) for a in [expected, *aliases]) and bool(g)


# Facts whose NAME says they are an id, number, amount or date must be copied exactly.
# Every other fact (product, description, payment method...) only needs to carry the same meaning.
EXACT_TOKENS = {"id", "ids", "order", "booking", "pnr", "ticket", "claim", "policy", "consumer", "phone", "mobile",
                "number", "no", "amount", "price", "date", "time", "account", "reference", "docket", "transaction",
                "invoice", "imei", "serial"}


def is_exact_fact(name: str) -> bool:
    tokens = [t for t in re.split(r"[\W_]+", name.casefold()) if t]
    return any(t in EXACT_TOKENS or (len(t) > 2 and t.endswith("id")) for t in tokens)


def _tokens(s: str) -> list[str]:
    return [t for t in re.split(r"[\W_]+", s.casefold()) if len(t) >= 3]


def _same_meaning(value: str, message: str) -> bool:
    """Cheap meaning check, no AI call: some word of the value matches a word of the message
    (spelling slips like 'greeen' vs 'green' allowed). Lenient on purpose: Phase 9 adds a stronger judge."""
    msg_tokens = _tokens(message)
    for t in _tokens(value):
        if any(difflib.SequenceMatcher(None, t, m).ratio() >= 0.8 for m in msg_tokens):
            return True
    return False


def fact_ok(name: str, value: str, message: str, strict: bool) -> bool:
    if _norm(value) in _norm(message):
        return True
    if strict or is_exact_fact(name):
        return False
    return _same_meaning(value, message)


def _all_strings(obj) -> list[str]:
    if isinstance(obj, str):
        return [obj]
    if isinstance(obj, list):
        return [s for x in obj for s in _all_strings(x)]
    if isinstance(obj, dict):
        return [s for x in obj.values() for s in _all_strings(x)]
    return []


@dataclass
class Result:
    id: str
    language: str
    category: str
    checks: dict[str, bool] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    @property
    def correct(self) -> bool:
        """The headline score: company, category, user_goal match and no invented facts."""
        return all(self.checks[k] for k in ("company", "category", "user_goal", "facts_grounded"))

    @property
    def passed(self) -> bool:
        """Headline score plus the safety and behaviour checks."""
        return all(self.checks.values())


def evaluate(problem: dict, resp: UnderstandResponse, strict: bool = False) -> Result:
    exp = problem["expected"]
    case = resp.case
    res = Result(problem["id"], problem["language"], exp["category"])

    res.checks["company"] = _company_ok(exp["company"], exp.get("company_aliases", []), case.company)
    # A different category is accepted only if the test says so AND the AI admitted it was unsure.
    low = case.category_confidence.value == "low"
    res.checks["category"] = case.category.value == exp["category"] or (
        low and case.category.value in exp.get("category_alternatives_if_low", []))
    res.checks["user_goal"] = case.user_goal.value == exp["user_goal"]

    # details_known may only hold facts that are really in the user's message.
    bad = [f for f in case.details_known if not fact_ok(f.name, f.value, problem["message"], strict)]
    res.checks["facts_grounded"] = not bad
    res.notes += [f"invented fact: {f.name}={f.value!r}" for f in bad]

    # Missing details must be asked, never guessed.
    asks = bool(resp.follow_up_question)
    res.checks["asks_when_missing"] = asks if (case.details_missing or case.company is None) else True
    res.checks["low_confidence_asks"] = asks if low else True
    if problem.get("must_ask"):
        res.checks["asks_when_needed"] = asks
    if problem.get("expect_other_issues"):
        res.checks["other_issues_found"] = len(case.other_issues) >= 1

    card = problem.get("card_in_message")
    if card:
        digits = re.sub(r"\D", "", " ".join(_all_strings(resp.model_dump(mode="json"))))
        res.checks["no_card_leak"] = card not in digits and card[:12] not in digits
    return res


def score_tables(results: list[Result]) -> str:
    def table(title: str, key) -> str:
        groups: dict[str, list[Result]] = defaultdict(list)
        for r in results:
            groups[key(r)].append(r)
        lines = [f"### {title}", "", "| Group | Problems | Correct | Accuracy | Fully passed |", "|---|---|---|---|---|"]
        for g in sorted(groups):
            rs = groups[g]
            c = sum(r.correct for r in rs)
            p = sum(r.passed for r in rs)
            lines.append(f"| {g} | {len(rs)} | {c} | {c / len(rs):.0%} | {p}/{len(rs)} |")
        c = sum(r.correct for r in results)
        p = sum(r.passed for r in results)
        lines.append(f"| **All** | {len(results)} | {c} | {c / len(results):.0%} | {p}/{len(results)} |")
        return "\n".join(lines)

    return "\n\n".join([
        table("Accuracy by language", lambda r: r.language),
        table("Accuracy by category", lambda r: r.category),
    ])


def redaction_selfcheck(problems: list[dict]) -> list[str]:
    """Problems whose card number would NOT be removed by the safety guard."""
    out = []
    for p in problems:
        if p.get("card_in_message"):
            clean, _ = redact(p["message"])
            if re.sub(r"\D", "", clean).find(p["card_in_message"][:12]) != -1:
                out.append(p["id"])
    return out


def baseline_markdown(problems: list[dict], responses: dict, meta: dict, stale: list[str] | None = None) -> tuple[str, list[Result], list[Result]]:
    """Score the same answers two ways and build docs/results/baseline-phase1.md.
    strict = every fact copied exactly. meaning = exact only for ids, numbers, amounts, dates; same meaning is enough otherwise."""
    strict = [evaluate(p, responses[p["id"]], strict=True) for p in problems]
    meaning = [evaluate(p, responses[p["id"]], strict=False) for p in problems]
    n = len(problems)
    sc, mc = sum(r.correct for r in strict), sum(r.correct for r in meaning)
    sp, mp = sum(r.passed for r in strict), sum(r.passed for r in meaning)
    md = ["# Phase 1 baseline (understand endpoint)", "",
          f"- Date: {meta['date']}", f"- Provider: `{meta['provider']}`; model: `{meta['model']}`",
          f"- Problems: {n}",
          "- Same answers, scored two ways (no new API calls for the second):", "",
          "| Rule | Correct (company, category, goal, facts) | Fully passed (plus safety and asking checks) |", "|---|---|---|",
          f"| **Meaning-based (current rule)** | **{mc}/{n} ({mc / n:.0%})** | {mp}/{n} |",
          f"| Strict (old rule: every fact copied exactly) | {sc}/{n} ({sc / n:.0%}) | {sp}/{n} |", "",
          "Meaning-based rule: ids, order/booking/claim numbers, phone numbers, amounts and dates must be copied exactly. "
          "Other facts (product names, descriptions, payment method names) pass if they keep the same meaning "
          "(fixed typos and translated words are fine). The check is a cheap word-overlap test, so it is lenient: "
          "Phase 9 should add a stronger judge.", ""]
    if stale:
        md += [f"- **{len(stale)} answers carried over from an earlier run (not re-run):** {', '.join(stale)}", ""]
    md += ["## Meaning-based (current rule)", "", score_tables(meaning), "", "### Failures (meaning-based)", ""]
    fails = [r for r in meaning if not r.passed]
    md += [f"- `{r.id}`: " + ", ".join(k for k, v in r.checks.items() if not v)
           + ((" | " + "; ".join(r.notes)) if r.notes else "") for r in fails] or ["- none"]
    md += ["", "## Strict (old rule), for comparison", "", score_tables(strict), "", "### Failures (strict)", ""]
    fails = [r for r in strict if not r.passed]
    md += [f"- `{r.id}`: " + ", ".join(k for k, v in r.checks.items() if not v)
           + ((" | " + "; ".join(r.notes)) if r.notes else "") for r in fails] or ["- none"]
    return "\n".join(md) + "\n", strict, meaning
