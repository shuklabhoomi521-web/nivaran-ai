from app.evaluation import evaluate, score_tables
from app.models.case import UnderstandResponse

PROBLEM = {"id": "x-1", "language": "english", "message": "Swiggy order 4839201 came cold, refund please",
           "expected": {"company": "Swiggy", "category": "food_delivery", "user_goal": "refund"}}


def resp(**over):
    case = {"company": "Swiggy", "category": "food_delivery", "category_confidence": "high", "problem_summary": "s", "user_goal": "refund",
            "details_known": [{"name": "order_id", "value": "4839201"}], "details_missing": [],
            "user_language": "english", "urgency": "medium", "other_issues": []}
    follow = over.pop("follow_up_question", None)
    case.update(over)
    return UnderstandResponse(case=case, follow_up_question=follow, redacted=[])


def test_correct_case_passes():
    r = evaluate(PROBLEM, resp())
    assert r.correct and r.passed


def test_wrong_goal_fails():
    assert not evaluate(PROBLEM, resp(user_goal="replace")).correct


def test_invented_fact_is_caught():
    r = evaluate(PROBLEM, resp(details_known=[{"name": "order_id", "value": "9999999"}]))
    assert not r.checks["facts_grounded"] and not r.correct


def test_guessing_company_when_unclear_fails():
    p = dict(PROBLEM, expected={"company": None, "category": "food_delivery", "user_goal": "refund"},
             must_ask=True)
    r = evaluate(p, resp())
    assert not r.checks["company"]


def test_must_ask_needs_a_question():
    p = dict(PROBLEM, expected={"company": None, "category": "food_delivery", "user_goal": "refund"},
             must_ask=True)
    no_q = evaluate(p, resp(company=None, details_missing=["company"]))
    with_q = evaluate(p, resp(company=None, details_missing=["company"], follow_up_question="Which company?"))
    assert not no_q.checks["asks_when_needed"]
    assert with_q.passed


def test_card_leak_is_caught():
    p = dict(PROBLEM, message="card 4111 1111 1111 1111 " + PROBLEM["message"], card_in_message="4111111111111111")
    leaked = evaluate(p, resp(problem_summary="paid with 4111111111111111"))
    assert not leaked.checks["no_card_leak"]
    assert evaluate(p, resp()).checks["no_card_leak"]


def test_alias_matching_and_tables():
    p = dict(PROBLEM, expected={"company": "TNEB", "company_aliases": ["TANGEDCO"], "category": "utilities",
                                "user_goal": "info"})
    r = evaluate(p, resp(company="TANGEDCO", category="utilities", user_goal="info", details_known=[]))
    assert r.checks["company"]
    table = score_tables([r])
    assert "Accuracy by language" in table and "Accuracy by category" in table


VAGUE = {"id": "v-1", "language": "tamil", "message": "ticket cancel panniten, refund innum varala",
         "expected": {"company": None, "category": "other", "user_goal": "refund",
                      "category_alternatives_if_low": ["railways"]}, "must_ask": True}


def test_alternative_category_accepted_only_when_low_confidence_and_asking():
    ok = evaluate(VAGUE, resp(company=None, category="railways", category_confidence="low", user_goal="refund",
                              details_known=[], details_missing=["company"],
                              follow_up_question="Which ticket is this?"))
    assert ok.passed


def test_alternative_category_rejected_when_sure():
    r = evaluate(VAGUE, resp(company=None, category="railways", category_confidence="high", user_goal="refund",
                             details_known=[], details_missing=["company"], follow_up_question="Which?"))
    assert not r.checks["category"]


def test_low_confidence_without_a_question_fails():
    r = evaluate(VAGUE, resp(company=None, category="railways", category_confidence="low", user_goal="refund",
                             details_known=[], details_missing=[]))
    assert not r.checks["low_confidence_asks"]
