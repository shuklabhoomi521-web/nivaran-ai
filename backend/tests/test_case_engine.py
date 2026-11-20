from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.api import tracked
from app.cases import engine
from app.cases.models import CaseState, Event, EventKind, Rung
from app.cases.store import CaseStore
from app.directory.lookup import find_company
from app.main import app
from app.models.case import Case, Category, Confidence, Fact, Language, Urgency, UserGoal

D0 = date(2026, 12, 5)


def understood(company="Swiggy", category=Category.food_delivery):
    return Case(company=company, category=category, category_confidence=Confidence.high, problem_summary="Order arrived cold, no refund.",
                user_goal=UserGoal.refund, details_known=[Fact(name="order_id", value="4839201")], details_missing=[],
                user_language=Language.english, urgency=Urgency.medium, other_issues=[])


def contact(rung, on=D0):
    return Event(on=on, kind=EventKind.contacted, rung=rung, channel="email", text="sent")


def test_new_case_needs_a_company_and_keeps_only_user_facts():
    c = engine.new_case(understood(), D0, "c1")
    assert c.state == CaseState.new and c.facts[0].value == "4839201" and c.created_on == D0
    with pytest.raises(engine.CaseError):
        engine.new_case(understood(company=None), D0)


def test_apply_never_changes_the_old_case_and_moves_state():
    c = engine.new_case(understood(), D0, "c1")
    c2 = engine.apply(c, contact(Rung.first_contact))
    assert c.state == CaseState.new and c.events == []                      # the old object is untouched
    assert c2.state == CaseState.waiting and len(c2.events) == 1
    c3 = engine.apply(c2, contact(Rung.grievance_officer, D0 + timedelta(days=7)))
    assert c3.state == CaseState.escalated
    c4 = engine.apply(c3, contact(Rung.appellate, D0 + timedelta(days=15)))
    assert c4.state == CaseState.escalated


def test_rules_are_enforced():
    c = engine.apply(engine.new_case(understood(), D0, "c1"), contact(Rung.first_contact))
    with pytest.raises(engine.CaseError):
        engine.apply(c, contact(Rung.first_contact))                         # same step twice
    with pytest.raises(engine.CaseError):
        engine.apply(c, Event(on=D0, kind=EventKind.contacted))              # a contact must name its rung
    with pytest.raises(engine.CaseError):
        engine.apply(c, Event(on=D0 - timedelta(days=1), kind=EventKind.note))   # older than the case
    done = engine.apply(c, Event(on=D0 + timedelta(days=2), kind=EventKind.resolved))
    assert done.state == CaseState.resolved and not done.is_open
    with pytest.raises(engine.CaseError):
        engine.apply(done, contact(Rung.follow_up))                          # nothing can be added after it is solved


def test_ladder_dates_are_day_0_3_7_15():
    c = engine.new_case(understood(), D0, "c1")
    assert [engine.due_date(c, r) - D0 for r in engine.ORDER] == [timedelta(days=d) for d in (0, 3, 7, 15, 15)]
    assert [r["status"] for r in engine.reminders(c, D0)] == ["due", "upcoming", "upcoming", "upcoming", "upcoming"]
    assert [r["status"] for r in engine.reminders(c, D0 + timedelta(days=8))] == ["due", "due", "due", "upcoming", "upcoming"]


def test_next_action_walks_the_ladder_using_the_directory():
    sw = find_company("Swiggy")
    c = engine.new_case(understood(), D0, "c1")
    a = engine.next_action(c, D0, sw)
    assert a.rung == Rung.first_contact and a.days_overdue == 0 and a.target_value and a.source_url and a.source_quote
    assert a.target_value == "grievances@swiggy.in" and "grievance address" in a.note       # Swiggy lists no support email or phone
    c = engine.apply(c, contact(Rung.first_contact))
    early = engine.next_action(c, D0 + timedelta(days=1), sw)
    assert early.rung == Rung.follow_up and "Nothing is due yet" in early.reason
    late = engine.next_action(c, D0 + timedelta(days=5), sw)
    assert late.rung == Rung.follow_up and late.days_overdue == 2 and "follow-up" in late.reason
    c = engine.apply(c, contact(Rung.follow_up, D0 + timedelta(days=3)))
    g = engine.next_action(c, D0 + timedelta(days=7), sw)
    assert g.rung == Rung.grievance_officer and g.target_value == "grievances@swiggy.in"


def test_missing_officer_or_appellate_falls_up_to_the_regulator_and_says_so():
    sw = find_company("Swiggy")                          # no appellate authority in the directory
    c = engine.new_case(understood(), D0, "c1")
    c = engine.apply(c, contact(Rung.first_contact))
    c = engine.apply(c, contact(Rung.follow_up, D0 + timedelta(days=3)))
    c = engine.apply(c, contact(Rung.grievance_officer, D0 + timedelta(days=7)))
    a = engine.next_action(c, D0 + timedelta(days=15), sw)
    assert a.rung == Rung.regulator and a.fell_back_from == Rung.appellate and a.channel == "portal"
    assert a.target_value.startswith("https://") and a.source_quote
    # a bank with no verified grievance email jumps over to the regulator: RBI
    nobody = engine.new_case(understood("Unknown Bank", Category.banking_upi), D0, "c2")
    nobody = engine.apply(nobody, contact(Rung.first_contact))
    nobody = engine.apply(nobody, contact(Rung.follow_up, D0 + timedelta(days=3)))
    r = engine.next_action(nobody, D0 + timedelta(days=9), None)
    assert r.rung == Rung.regulator and r.fell_back_from == Rung.grievance_officer and "RBI" in r.target_label


def test_a_step_skipped_upward_is_not_repeated_and_the_ladder_ends():
    sw = find_company("Swiggy")
    c = engine.new_case(understood(), D0, "c1")
    c = engine.apply(c, contact(Rung.first_contact))
    c = engine.apply(c, contact(Rung.regulator, D0 + timedelta(days=4)))      # the user went straight to the portal
    assert engine.next_action(c, D0 + timedelta(days=20), sw) is None
    assert all(r["status"] == "done" for r in engine.reminders(c, D0 + timedelta(days=20)))
    with pytest.raises(engine.CaseError):
        engine.apply(c, contact(Rung.grievance_officer, D0 + timedelta(days=5)))


def test_closed_cases_have_no_next_action():
    sw = find_company("Swiggy")
    c = engine.apply(engine.new_case(understood(), D0, "c1"), Event(on=D0, kind=EventKind.closed))
    assert engine.next_action(c, D0 + timedelta(days=30), sw) is None
    assert {r["status"] for r in engine.reminders(c, D0)} == {"closed"}


def test_store_round_trip_and_delete(tmp_path):
    s = CaseStore(tmp_path / "cases.json")
    c = engine.apply(engine.new_case(understood(), D0, "c1"), contact(Rung.first_contact))
    s.save(c)
    assert s.get("c1") == c and [x.id for x in s.list()] == ["c1"] and s.get("nope") is None
    assert s.delete("c1") and not s.delete("c1") and s.list() == []


def test_api_flow(tmp_path, monkeypatch):
    store = CaseStore(tmp_path / "cases.json")
    app.dependency_overrides[tracked.get_store] = lambda: store
    monkeypatch.setattr(tracked, "_today", lambda: D0 + timedelta(days=4))
    try:
        cl = TestClient(app)
        r = cl.post("/tracked-cases", json={"case": understood().model_dump(mode="json")})
        assert r.status_code == 200
        cid = r.json()["id"]
        assert cl.post("/tracked-cases", json={"case": understood("No Such Company").model_dump(mode="json")}).status_code == 422
        n = cl.get(f"/tracked-cases/{cid}/next").json()
        assert n["action"]["rung"] == "first_contact" and len(n["reminders"]) == 5
        ev = {"on": (D0 + timedelta(days=4)).isoformat(), "kind": "contacted", "rung": "first_contact", "channel": "email", "text": "sent"}
        assert cl.post(f"/tracked-cases/{cid}/events", json=ev).status_code == 200
        assert cl.post(f"/tracked-cases/{cid}/events", json=ev).status_code == 409           # repeated step
        assert cl.get(f"/tracked-cases/{cid}/next").json()["action"]["rung"] == "follow_up"
        assert cl.get("/tracked-cases/zzz").status_code == 404
        assert cl.delete(f"/tracked-cases/{cid}").status_code == 200 and cl.get(f"/tracked-cases/{cid}").status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_company_with_a_support_line_uses_it_first_and_unknown_company_says_nothing_is_verified():
    airtel = find_company("Airtel")
    c = engine.new_case(understood("Airtel", Category.telecom), D0, "c9")
    a = engine.next_action(c, D0, airtel)
    assert a.target_value and a.source_quote and a.note is None
    unknown = engine.next_action(engine.new_case(understood("Nobody Ltd", Category.other), D0, "c10"), D0, None)
    assert unknown.target_value is None and unknown.rung == Rung.first_contact
