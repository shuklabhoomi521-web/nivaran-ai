from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.api import letters as letters_api
from app.api import tracked
from app.cases import engine
from app.cases.models import Event, EventKind, Rung
from app.cases.store import CaseStore
from app.directory.lookup import find_company
from app.letters import outbox
from app.letters.compose import LetterError, allowed_recipients, compose
from app.letters.outbox import DraftStatus, DraftStore, SmtpSender
from app.main import app
from app.models.case import Case, Category, Confidence, Fact, Language, Urgency, UserGoal

D0 = date(2026, 12, 5)
SW = find_company("Swiggy")


def understood(facts=None, company="Swiggy", category=Category.food_delivery):
    return Case(company=company, category=category, category_confidence=Confidence.high, problem_summary="Order arrived cold, no refund.",
                user_goal=UserGoal.refund, details_known=facts if facts is not None else [Fact(name="order_id", value="4839201")],
                details_missing=[], user_language=Language.english, urgency=Urgency.medium, other_issues=[])


def case(**kw):
    return engine.new_case(understood(**kw), D0, "c1", user_name="Bhoomi Shukla")


class FakeSender:
    def __init__(self):
        self.sent = []

    def send(self, to, subject, body):
        self.sent.append((to, subject, body))
        return "<fake-id@test>"


def draft_for(c, day=D0):
    return outbox.new_draft(c.id, compose(c, engine.next_action(c, day, SW), day), day)


def test_letter_uses_only_what_the_user_gave():
    c = case()
    a = engine.next_action(c, D0, SW)
    L = compose(c, a, D0)
    assert L.channel == "email" and L.to == "grievances@swiggy.in" and L.rung == Rung.first_contact
    assert "Order arrived cold, no refund." in L.body and "order id: 4839201" in L.body and "a refund" in L.body
    assert "Bhoomi Shukla" in L.body and "Case reference: c1" in L.body
    for forbidden in ("Consumer Protection", "legal", "court", "within 24 hours", "I demand", "compensation"):
        assert forbidden not in L.body                      # no laws, deadlines or threats we cannot back up


def test_follow_up_and_escalation_letters_carry_the_history():
    c = case()
    c = engine.apply(c, Event(on=D0, kind=EventKind.contacted, rung=Rung.first_contact, channel="email", text="first email"))
    f = compose(c, engine.next_action(c, D0 + timedelta(days=3), SW), D0)
    assert "I wrote to you on 5 December 2026" in f.body
    c = engine.apply(c, Event(on=D0 + timedelta(days=3), kind=EventKind.contacted, rung=Rung.follow_up, channel="email", text="reminder", docket="TKT-77"))
    g = compose(c, engine.next_action(c, D0 + timedelta(days=7), SW), D0)
    assert "Grievance Officer" in g.body and "5 December 2026: email (first email)" in g.body and "TKT-77" in g.body


def test_portal_step_produces_complaint_text_for_the_user_to_file():
    c = case()
    for r, d in ((Rung.first_contact, 0), (Rung.follow_up, 3), (Rung.grievance_officer, 7)):
        c = engine.apply(c, Event(on=D0 + timedelta(days=d), kind=EventKind.contacted, rung=r, channel="email"))
    a = engine.next_action(c, D0 + timedelta(days=15), SW)
    L = compose(c, a, D0)
    assert L.channel == "portal" and L.to.startswith("https://") and "Complaint against Swiggy" in L.body


def test_no_verified_contact_means_no_letter():
    c = engine.new_case(understood(company="Nobody Ltd", category=Category.other), D0, "c2")
    with pytest.raises(LetterError):
        compose(c, engine.next_action(c, D0, None), D0)


def test_payment_data_in_the_facts_blocks_the_letter():
    c = case(facts=[Fact(name="note", value="my card 4111 1111 1111 1111 was charged")])
    with pytest.raises(LetterError):
        compose(c, engine.next_action(c, D0, SW), D0)


def test_nothing_is_sent_without_approval_and_edits_cancel_approval():
    c = case()
    d = draft_for(c)
    s = FakeSender()
    with pytest.raises(LetterError):
        outbox.send(d, SW, s, D0)                                    # pending: refused
    d = outbox.approve(d, D0)
    edited = d.model_copy(update={"body": d.body + "\nExtra line"})  # changed after approval
    with pytest.raises(LetterError):
        outbox.send(edited, SW, s, D0)
    with pytest.raises(LetterError):
        outbox.edit(d, "x", None)                                    # approved drafts cannot be edited
    sent = outbox.send(d, SW, s, D0)
    assert sent.status == DraftStatus.sent and sent.message_id and s.sent[0][0] == "grievances@swiggy.in"
    with pytest.raises(LetterError):
        outbox.send(sent, SW, s, D0)                                 # a sent draft is not sent twice
    assert len(s.sent) == 1


def test_recipient_must_be_in_the_directory_and_payment_data_is_blocked_at_send():
    d = outbox.approve(draft_for(case()), D0)
    stranger = d.model_copy(update={"to": "someone@elsewhere.test"})
    stranger = stranger.model_copy(update={"approved_hash": outbox.text_hash(stranger.subject, stranger.body, stranger.to)})
    with pytest.raises(LetterError):
        outbox.send(stranger, SW, FakeSender(), D0)                  # approved, but not a directory address
    assert "grievances@swiggy.in" in allowed_recipients(SW) and allowed_recipients(None) == set()
    bad = d.model_copy(update={"body": "my CVV 123 is here"})
    bad = bad.model_copy(update={"approved_hash": outbox.text_hash(bad.subject, bad.body, bad.to)})
    with pytest.raises(LetterError):
        outbox.send(bad, SW, FakeSender(), D0)


def test_portal_drafts_are_never_sent_by_the_app():
    c = case()
    for r, dd in ((Rung.first_contact, 0), (Rung.follow_up, 3), (Rung.grievance_officer, 7)):
        c = engine.apply(c, Event(on=D0 + timedelta(days=dd), kind=EventKind.contacted, rung=r, channel="email"))
    d = outbox.approve(draft_for(c, D0 + timedelta(days=15)), D0)
    with pytest.raises(LetterError):
        outbox.send(d, SW, FakeSender(), D0)


class FakeSMTP:
    log = []

    def __init__(self, host, port, timeout=0):
        FakeSMTP.log.append(("connect", host, port))

    def starttls(self, context=None):
        FakeSMTP.log.append(("starttls",))

    def login(self, user, password):
        FakeSMTP.log.append(("login", user))

    def send_message(self, msg):
        FakeSMTP.log.append(("send", msg["To"], msg["Subject"], msg["From"]))

    def quit(self):
        FakeSMTP.log.append(("quit",))


def test_smtp_sender_talks_to_a_fake_server(monkeypatch):
    monkeypatch.delenv("SMTP_USER", raising=False)        # never depend on the developer's real .env
    monkeypatch.delenv("SMTP_PASSWORD", raising=False)
    FakeSMTP.log = []
    s = SmtpSender(host="smtp.test", port=587, user="me@test.example", password="app-password-not-real", from_name="Bhoomi", factory=FakeSMTP)
    mid = s.send("grievances@swiggy.in", "Subject", "Body")
    assert mid.endswith("@nivaran.local>") and [x[0] for x in FakeSMTP.log] == ["connect", "starttls", "login", "send", "quit"]
    assert FakeSMTP.log[3][1:] == ("grievances@swiggy.in", "Subject", "Bhoomi <me@test.example>")
    with pytest.raises(LetterError):
        SmtpSender(host="smtp.test", user="", password="", factory=FakeSMTP)


def test_api_flow_from_draft_to_sent(tmp_path, monkeypatch):
    cases, drafts, sender = CaseStore(tmp_path / "c.json"), DraftStore(tmp_path / "d.json"), FakeSender()
    app.dependency_overrides[tracked.get_store] = lambda: cases
    app.dependency_overrides[letters_api.get_drafts] = lambda: drafts
    app.dependency_overrides[letters_api.get_sender] = lambda: sender
    monkeypatch.setattr(tracked, "_today", lambda: D0)
    monkeypatch.setattr(letters_api, "_today", lambda: D0)
    try:
        cl = TestClient(app)
        cid = cl.post("/tracked-cases", json={"case": understood().model_dump(mode="json"), "user_name": "Bhoomi Shukla", "consent": True, "adult": True}).json()["id"]
        d = cl.post(f"/tracked-cases/{cid}/drafts").json()
        assert d["status"] == "pending" and "Bhoomi Shukla" in d["body"]
        assert cl.post(f"/drafts/{d['id']}/send").status_code == 409 and sender.sent == []          # not approved: refused
        assert cl.patch(f"/drafts/{d['id']}", json={"body": d["body"] + "\nPlease treat this as urgent."}).status_code == 200
        assert cl.post(f"/drafts/{d['id']}/approve").json()["status"] == "approved"
        r = cl.post(f"/drafts/{d['id']}/send")
        assert r.status_code == 200 and r.json()["draft"]["status"] == "sent" and r.json()["case"]["state"] == "waiting"
        assert len(sender.sent) == 1 and "urgent" in sender.sent[0][2]
        assert cl.post(f"/drafts/{d['id']}/send").status_code == 409 and len(sender.sent) == 1     # never twice
        assert cl.get(f"/tracked-cases/{cid}/next").json()["action"]["rung"] == "follow_up"
        assert cl.get("/drafts/zzz/x").status_code == 404 and len(cl.get(f"/tracked-cases/{cid}/drafts").json()) == 1
    finally:
        app.dependency_overrides.clear()
