"""One whole journey through the real API with fakes for the outside world (mail server, inbox, clock):
consent, create, first letter, approval, send, a reply arrives, the ladder walks to the regulator's portal, the kit, then delete.
It also checks that nothing private is readable in the files on disk."""
from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.api import letters as letters_api
from app.api import replies as replies_api
from app.api import tracked
from app.cases.store import CaseStore
from app.letters.outbox import DraftStore
from app.main import app
from app.replies.matcher import InboxMessage

D0 = date(2026, 12, 5)


class Clock:
    today = D0


class FakeSender:
    def __init__(self):
        self.sent = []

    def send(self, to, subject, body):
        self.sent.append((to, subject, body))
        return f"<sent-{len(self.sent)}@nivaran.local>"


class FakeInbox:
    def __init__(self):
        self.messages = []

    def fetch_since(self, since, limit=300):
        return self.messages


def test_whole_journey(tmp_path, monkeypatch):
    cases, drafts, sender, inbox, clock = CaseStore(tmp_path / "c.bin"), DraftStore(tmp_path / "d.bin"), FakeSender(), FakeInbox(), Clock()
    app.dependency_overrides[tracked.get_store] = lambda: cases
    app.dependency_overrides[letters_api.get_drafts] = lambda: drafts
    app.dependency_overrides[letters_api.get_sender] = lambda: sender
    app.dependency_overrides[replies_api.get_inbox] = lambda: inbox
    for mod in (tracked, letters_api, replies_api):
        monkeypatch.setattr(mod, "_today", lambda: clock.today)
    try:
        cl = TestClient(app)
        understood = {"company": "Swiggy", "category": "food_delivery", "category_confidence": "high", "problem_summary": "Cold order, no refund, journey-test.",
                      "user_goal": "refund", "details_known": [{"name": "order_id", "value": "4839201"}], "details_missing": [],
                      "user_language": "english", "urgency": "medium", "other_issues": []}
        assert "never ask for" in cl.get("/tracked-cases/consent-notice").json()["text"]
        assert cl.post("/tracked-cases", json={"case": understood}).status_code == 422                       # no consent: refused
        cid = cl.post("/tracked-cases", json={"case": understood, "user_name": "Journey Tester", "consent": True, "adult": True}).json()["id"]

        # day 0: first message goes to the verified grievance address after the user approves it
        d = cl.post(f"/tracked-cases/{cid}/drafts").json()
        assert d["to"] == "grievances@swiggy.in" and "journey-test" in d["body"]
        cl.post(f"/drafts/{d['id']}/approve")
        sent = cl.post(f"/drafts/{d['id']}/send").json()
        assert sent["case"]["state"] == "waiting" and sender.sent[0][0] == "grievances@swiggy.in"

        # day 1: the company replies to that exact message (matched by Message-ID)
        clock.today = D0 + timedelta(days=1)
        inbox.messages = [InboxMessage(message_id="<reply-1@swiggy.in>", from_addr="Swiggy <grievances@swiggy.in>", subject="Re: Complaint",
                                       on=clock.today, snippet="Ticket number 556677 has been created.", in_reply_to=sent["draft"]["message_id"])]
        r = cl.post(f"/tracked-cases/{cid}/check-replies").json()
        assert len(r["new_replies"]) == 1 and r["new_replies"][0]["strength"] == "strong" and r["new_replies"][0]["auto_acknowledgement"]
        assert cl.post(f"/tracked-cases/{cid}/check-replies").json()["new_replies"] == []                  # not added twice

        # day 3 to 15: nothing solved, so the ladder moves up and the app shows the next step each time
        clock.today = D0 + timedelta(days=3)
        assert cl.get(f"/tracked-cases/{cid}/next").json()["action"]["rung"] == "follow_up"
        for rung, day in (("follow_up", 3), ("grievance_officer", 7)):
            cl.post(f"/tracked-cases/{cid}/events", json={"on": (D0 + timedelta(days=day)).isoformat(), "kind": "contacted", "rung": rung, "channel": "email"})
        clock.today = D0 + timedelta(days=15)
        nxt = cl.get(f"/tracked-cases/{cid}/next").json()
        assert nxt["action"]["rung"] == "regulator" and nxt["action"]["channel"] == "portal" and nxt["action"]["fell_back_from"] == "appellate"

        # the portal kit has sourced steps and a ready complaint text; the user files it by hand and records the docket
        kit = cl.get(f"/tracked-cases/{cid}/portal-kit").json()
        assert kit["regulator_key"] == "nch" and all(s["source"]["quote"] for s in kit["steps"]) and "journey-test" in kit["complaint_text"]
        ev = {"on": clock.today.isoformat(), "kind": "contacted", "rung": "regulator", "channel": "portal", "text": "filed, docket NCH-1", "docket": "NCH-1"}
        assert cl.post(f"/tracked-cases/{cid}/events", json=ev).status_code == 200
        assert cl.get(f"/tracked-cases/{cid}/next").json()["action"] is None                                # the ladder is finished

        # privacy: nothing readable on disk, and the user can delete everything
        raw = (tmp_path / "c.bin").read_bytes() + (tmp_path / "d.bin").read_bytes()
        assert b"Journey Tester" not in raw and b"4839201" not in raw and b"journey-test" not in raw
        assert cl.delete(f"/tracked-cases/{cid}").status_code == 200 and cl.get(f"/tracked-cases/{cid}").status_code == 404
        assert len(sender.sent) == 1                                                                         # exactly one email left the app, after approval
    finally:
        app.dependency_overrides.clear()
