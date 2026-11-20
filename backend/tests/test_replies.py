from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.api import letters as letters_api
from app.api import replies as replies_api
from app.api import tracked
from app.cases import engine
from app.cases.models import CaseState, EventKind
from app.cases.store import CaseStore
from app.directory.lookup import find_company
from app.letters.outbox import DraftStore
from app.main import app
from app.models.case import Case, Category, Confidence, Fact, Language, Urgency, UserGoal
from app.replies import inbox as inbox_mod
from app.replies import matcher
from app.replies.matcher import InboxMessage, Strength

D0 = date(2026, 12, 5)
SW = find_company("Swiggy")


def case():
    u = Case(company="Swiggy", category=Category.food_delivery, category_confidence=Confidence.high, problem_summary="Cold order.",
             user_goal=UserGoal.refund, details_known=[Fact(name="order_id", value="4839201")], details_missing=[],
             user_language=Language.english, urgency=Urgency.low, other_issues=[])
    return engine.new_case(u, D0, "c1", user_name="B")


def msg(mid="<m1>", frm="Swiggy Support <grievances@swiggy.in>", subject="Re: Complaint", snippet="We are looking into it.", on=D0 + timedelta(days=1), **kw):
    return InboxMessage(message_id=mid, from_addr=frm, subject=subject, on=on, snippet=snippet, **kw)


def test_strong_match_by_our_message_id_and_by_case_reference():
    c = case()
    a = matcher.classify(c, msg(frm="x@elsewhere.test", in_reply_to="<sent-1>"), SW, {"<sent-1>"})
    assert a.strength == Strength.strong and "Message-ID" in a.reason
    b = matcher.classify(c, msg(frm="x@elsewhere.test", subject="Your case c1 update"), SW, set())
    assert b.strength == Strength.strong and "case reference" in b.reason


def test_weak_match_only_for_company_senders_and_never_for_strangers_or_old_mail():
    c = case()
    assert matcher.classify(c, msg(), SW, set()).strength == Strength.weak
    assert matcher.classify(c, msg(frm="someone@news.test"), SW, set()) is None
    assert matcher.classify(c, msg(on=D0 - timedelta(days=3)), SW, set()) is None          # older than the case
    assert matcher.classify(c, msg(), None, set()) is None                                  # unknown company: no sender match


def test_auto_acknowledgement_resolved_hint_and_docket():
    c = case()
    auto = matcher.classify(c, msg(subject="[Ticket #TKT-48213] Your ticket has been created", snippet="Thank you for contacting us."), SW, set())
    assert auto.auto_acknowledgement and not auto.looks_resolved and auto.docket and "48213" in auto.docket
    for phrase in ("Ticket number 556677 has been created.", "Your ticket TKT-1 was raised", "Your complaint has been registered.", "We have received your request."):
        assert matcher.classify(c, msg(snippet=phrase), SW, set()).auto_acknowledgement, phrase
    done = matcher.classify(c, msg(snippet="We have processed a refund of Rs 250 to your account."), SW, set())
    assert done.looks_resolved and not done.auto_acknowledgement


def test_track_adds_events_once_keeps_state_and_redacts():
    c = engine.apply(case(), engine.Event(on=D0, kind=EventKind.contacted, rung=engine.Rung.first_contact, channel="email"))
    m1 = msg(snippet="Please send your card 4111 1111 1111 1111 so we can refund")
    c2, new = matcher.track(c, [m1, msg(mid="<m2>", frm="stranger@x.test")], SW, set(), D0)
    assert len(new) == 1 and c2.state == CaseState.waiting                                  # a reply does not change the state
    ev = c2.events[-1]
    assert ev.kind == EventKind.reply_received and ev.source_id == "<m1>" and "4111" not in ev.text and "[CARD NUMBER REMOVED]" in ev.text
    c3, again = matcher.track(c2, [m1], SW, set(), D0)
    assert again == [] and len(c3.events) == len(c2.events)                                 # the same email is never added twice
    assert len(c.events) == 1                                                               # the old case object is untouched


RAW = (b"From: Swiggy Support <grievances@swiggy.in>\r\nTo: me@x.test\r\nSubject: =?utf-8?q?Re=3A_Complaint_c1?=\r\nDate: Sun, 06 Dec 2026 10:00:00 +0530\r\n"
       b"Message-ID: <abc@swiggy.in>\r\nIn-Reply-To: <sent-1@nivaran.local>\r\nReferences: <sent-1@nivaran.local>\r\n\r\n"
       b"We are sorry about this. Ticket number 889900 is created.\r\n\r\nOn Sat, 5 Dec 2026, B wrote:\r\n> old quoted text\r\n")


def test_parse_strips_quoted_text_and_reads_headers():
    m = inbox_mod.parse(RAW)
    assert m.message_id == "<abc@swiggy.in>" and m.on == date(2026, 12, 6) and m.in_reply_to == "<sent-1@nivaran.local>"
    assert "old quoted text" not in m.snippet and "Ticket number 889900" in m.snippet and m.subject == "Re: Complaint c1"


class FakeIMAP:
    calls = []

    def __init__(self, host):
        FakeIMAP.calls = [("connect", host)]

    def login(self, u, p):
        FakeIMAP.calls.append(("login", u))

    def select(self, box, readonly=False):
        FakeIMAP.calls.append(("select", box, readonly))
        return "OK", [b"1"]

    def search(self, charset, *crit):
        FakeIMAP.calls.append(("search", crit))
        return "OK", [b"1"]

    def fetch(self, num, spec):
        FakeIMAP.calls.append(("fetch", spec))
        return "OK", [(b"1 (BODY[] {10}", RAW), b")"]

    def logout(self):
        FakeIMAP.calls.append(("logout",))


def test_imap_reader_is_read_only():
    box = inbox_mod.ImapInbox(user="me@test.example", password="not-a-real-password", factory=FakeIMAP)
    out = box.fetch_since(D0)
    assert len(out) == 1
    names = [c[0] for c in FakeIMAP.calls]
    assert ("select", "INBOX", True) in FakeIMAP.calls                                       # opened read-only
    assert ("fetch", "(BODY.PEEK[])") in FakeIMAP.calls                                      # PEEK: does not mark mail as read
    assert set(names) <= {"connect", "login", "select", "search", "fetch", "logout"}         # no store, copy, delete or expunge


class FakeBox:
    def fetch_since(self, since, limit=300):
        return [inbox_mod.parse(RAW)]


def test_api_check_replies(tmp_path, monkeypatch):
    cases, drafts = CaseStore(tmp_path / "c.json"), DraftStore(tmp_path / "d.json")
    app.dependency_overrides[tracked.get_store] = lambda: cases
    app.dependency_overrides[letters_api.get_drafts] = lambda: drafts
    app.dependency_overrides[replies_api.get_inbox] = lambda: FakeBox()
    monkeypatch.setattr(tracked, "_today", lambda: D0)
    monkeypatch.setattr(replies_api, "_today", lambda: D0 + timedelta(days=1))
    try:
        cl = TestClient(app)
        cid = cl.post("/tracked-cases", json={"case": {"company": "Swiggy", "category": "food_delivery", "category_confidence": "high",
              "problem_summary": "Cold order.", "user_goal": "refund", "details_known": [], "details_missing": [], "user_language": "english",
              "urgency": "low", "other_issues": []}, "consent": True, "adult": True}).json()["id"]
        r = cl.post(f"/tracked-cases/{cid}/check-replies").json()
        assert len(r["new_replies"]) == 1 and r["new_replies"][0]["docket"] and r["case"]["events"][-1]["kind"] == "reply_received"
        assert cl.post(f"/tracked-cases/{cid}/check-replies").json()["new_replies"] == []     # second check adds nothing
        assert cl.post("/tracked-cases/zzz/check-replies").status_code == 404
    finally:
        app.dependency_overrides.clear()
