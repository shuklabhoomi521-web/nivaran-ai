from collections import Counter

from app.evaluation import load_problems, redaction_selfcheck

KNOWN_CATS = {"food_delivery", "ecommerce", "telecom", "banking_upi", "airlines", "railways",
              "cabs", "electronics_appliances", "insurance", "utilities", "other"}


def test_each_problem_is_well_formed():
    ids = set()
    for p in load_problems():
        assert p["id"] not in ids
        ids.add(p["id"])
        assert p["language"] in {"english", "hindi", "tamil", "hinglish"}
        assert p["message"].strip()
        assert p["expected"]["category"] in KNOWN_CATS
        assert {"company", "category", "user_goal"} <= p["expected"].keys()


def test_set_is_varied_and_hard():
    ps = load_problems()
    assert len(ps) >= 25
    assert {p["language"] for p in ps} == {"english", "hindi", "tamil", "hinglish"}
    assert len({p["expected"]["category"] for p in ps}) >= 8
    tags = Counter(t for p in ps for t in p.get("tags", []))
    assert tags["missing_details"] >= 3
    assert tags["two_problems"] >= 2
    assert tags["unclear_company"] >= 1
    assert tags["card_number"] >= 2


def test_every_card_in_the_set_is_caught_by_the_safety_guard():
    assert redaction_selfcheck(load_problems()) == []
