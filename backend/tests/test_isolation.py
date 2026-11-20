"""Per-person access: one person must never read, change, send from, delete, call about or even detect another person's case."""
import base64
import json
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.api import calls as calls_api
from app.api import letters as letters_api
from app.api import replies as replies_api
from app.api import speech as speech_api
from app.api import tracked
from app.cases import engine
from app.cases.store import CaseStore
from app.letters.outbox import DraftStore
from app.main import app
from app.replies import matcher
from app.replies.matcher import InboxMessage
from app.speech.base import Transcript
from app.users import LEGACY_OWNER, add_user, find_user, load_users, revoke_user
from tests.test_case_engine import understood
from tests.test_calls_api import Voice

D0 = date(2026, 12, 5)


class FakeSender:
    def __init__(self):
        self.sent = []

    def send(self, to, subject, body):
        self.sent.append(to)
        return "<id@nivaran.local>"


class FakeInbox:
    def __init__(self):
        self.messages = []

    def fetch_since(self, since, limit=300):
        return self.messages


class FakeSTT:
    def transcribe(self, audio, mime_type, language=None):
        return Transcript(text="hello", language="en-IN", provider="fake")


@pytest.fixture
def world(tmp_path, monkeypatch):
    monkeypatch.setenv("PILOT_USERS_FILE", str(tmp_path / "users.json"))
    monkeypatch.setenv("PHONE_ALLOWED_NUMBERS", "+919000000001")
    monkeypatch.delenv("NIVARAN_API_TOKEN", raising=False)
    a_id, a_tok = add_user("Volunteer A")
    b_id, b_tok = add_user("Volunteer B")
    cases, drafts, sender, inbox, voice = CaseStore(tmp_path / "c.bin"), DraftStore(tmp_path / "d.bin"), FakeSender(), FakeInbox(), Voice()
    app.dependency_overrides.update({tracked.get_store: lambda: cases, letters_api.get_drafts: lambda: drafts, letters_api.get_sender: lambda: sender,
                                     replies_api.get_inbox: lambda: inbox, calls_api.get_voice: lambda: voice.client(), speech_api.get_stt: lambda: FakeSTT()})
    for mod in (tracked, letters_api, replies_api, calls_api):
        monkeypatch.setattr(mod, "_today", lambda: D0)
    c = TestClient(app)
    yield {"c": c, "A": {"Authorization": f"Bearer {a_tok}"}, "B": {"Authorization": f"Bearer {b_tok}"}, "cases": cases, "drafts": drafts,
           "sender": sender, "inbox": inbox, "voice": voice, "tokens": (a_tok, b_tok), "path": tmp_path / "users.json"}
    app.dependency_overrides.clear()


def make_case(w, who="A"):
    body = {"case": understood().model_dump(mode="json"), "user_name": "Tester", "consent": True, "adult": True}
    r = w["c"].post("/tracked-cases", json=body, headers=w[who])
    assert r.status_code == 200
    return r.json()["id"]


def test_each_person_sees_only_their_own_cases(world):
    w, c = world, world["c"]
    a_case = make_case(w, "A")
    assert [x["id"] for x in c.get("/tracked-cases", headers=w["A"]).json()] == [a_case]
    assert c.get("/tracked-cases", headers=w["B"]).json() == []
    for method, path in (("get", f"/tracked-cases/{a_case}"), ("get", f"/tracked-cases/{a_case}/next"), ("get", f"/tracked-cases/{a_case}/portal-kit"),
                         ("get", f"/tracked-cases/{a_case}/drafts"), ("post", f"/tracked-cases/{a_case}/drafts"), ("delete", f"/tracked-cases/{a_case}"),
                         ("post", f"/tracked-cases/{a_case}/check-replies")):
        r = getattr(c, method)(path, headers=w["B"])
        assert r.status_code == 404, (method, path)
    ev = {"on": D0.isoformat(), "kind": "note", "text": "x"}
    assert c.post(f"/tracked-cases/{a_case}/events", json=ev, headers=w["B"]).status_code == 404
    assert c.get(f"/tracked-cases/{a_case}", headers=w["A"]).status_code == 200            # A still has it, untouched
    assert w["cases"].get(a_case).events == []


def test_a_foreign_case_looks_exactly_like_a_case_that_does_not_exist(world):
    w, c = world, world["c"]
    a_case = make_case(w, "A")
    foreign, missing = c.get(f"/tracked-cases/{a_case}", headers=w["B"]), c.get("/tracked-cases/nonexistent", headers=w["B"])
    assert foreign.status_code == missing.status_code == 404 and foreign.json() == missing.json()


def test_drafts_cannot_be_read_edited_approved_or_sent_by_someone_else(world):
    w, c = world, world["c"]
    a_case = make_case(w, "A")
    d = c.post(f"/tracked-cases/{a_case}/drafts", headers=w["A"]).json()
    unknown = c.post("/drafts/nope/approve", headers=w["B"])
    for method, path, body in (("patch", f"/drafts/{d['id']}", {"body": "hijack"}), ("post", f"/drafts/{d['id']}/approve", None),
                               ("post", f"/drafts/{d['id']}/reject", None), ("post", f"/drafts/{d['id']}/send", None)):
        r = getattr(c, method)(path, headers=w["B"], **({"json": body} if body else {}))
        assert r.status_code == 404 and r.json() == unknown.json(), path                  # same answer as a draft that never existed
    assert w["sender"].sent == [] and w["drafts"].get(d["id"]).status.value == "pending" and "hijack" not in w["drafts"].get(d["id"]).body
    assert c.post(f"/drafts/{d['id']}/approve", headers=w["A"]).status_code == 200
    assert c.post(f"/drafts/{d['id']}/send", headers=w["A"]).status_code == 200 and len(w["sender"].sent) == 1


def test_only_the_owner_can_place_calls_and_nobody_can_call_for_someone_elses_case(world, monkeypatch):
    w, c = world, world["c"]
    a_case = make_case(w, "A")
    p = c.get(f"/tracked-cases/{a_case}/call/preview", headers=w["A"]).json()
    assert p["can_start"] is False and "owner" in p["why_not"]
    assert c.post(f"/tracked-cases/{a_case}/call", json={"confirm": True}, headers=w["A"]).status_code == 403
    assert c.post(f"/tracked-cases/{a_case}/call/CA123/hangup", headers=w["A"]).status_code == 403
    assert c.get(f"/tracked-cases/{a_case}/call/events", headers=w["A"]).status_code == 403
    assert c.get(f"/tracked-cases/{a_case}/call/preview", headers=w["B"]).status_code == 404
    assert c.post(f"/tracked-cases/{a_case}/call", json={"confirm": True}, headers=w["B"]).status_code == 404
    assert w["voice"].requests == []                                                         # the voice server was never contacted
    monkeypatch.setenv("NIVARAN_API_TOKEN", "owner-secret-not-real")                        # the builder's own token
    owner = {"Authorization": "Bearer owner-secret-not-real"}
    assert c.get(f"/tracked-cases/{a_case}", headers=owner).status_code == 404               # even the owner does not see a volunteer's case by id
    own_case = c.post("/tracked-cases", json={"case": understood().model_dump(mode="json"), "consent": True, "adult": True}, headers=owner).json()["id"]
    assert c.post(f"/tracked-cases/{own_case}/call", json={"confirm": True}, headers=owner).status_code == 200


def test_legacy_cases_belong_to_the_owner_only(world, monkeypatch):
    w, c = world, world["c"]
    w["cases"].save(engine.new_case(understood(), D0, "legacy1"))                            # made before accounts: no owner id
    assert c.get("/tracked-cases/legacy1", headers=w["A"]).status_code == 404
    assert c.get("/tracked-cases", headers=w["A"]).json() == []
    monkeypatch.setenv("NIVARAN_API_TOKEN", "owner-secret-not-real")
    owner = {"Authorization": "Bearer owner-secret-not-real"}
    assert c.get("/tracked-cases/legacy1", headers=owner).status_code == 200 and [x["id"] for x in c.get("/tracked-cases", headers=owner).json()] == ["legacy1"]


def test_weak_reply_matches_are_for_the_owner_only(world, monkeypatch):
    w, c = world, world["c"]
    a_case = make_case(w, "A")
    msg = InboxMessage(message_id="<m1@swiggy.in>", from_addr="Swiggy <grievances@swiggy.in>", subject="About your other order", on=D0 + timedelta(days=1),
                       snippet="This is a message to the builder about something else.")
    w["inbox"].messages = [msg]
    assert c.post(f"/tracked-cases/{a_case}/check-replies", headers=w["A"]).json()["new_replies"] == []         # sender-only match is not shown to a volunteer
    strong = InboxMessage(message_id="<m2@swiggy.in>", from_addr="Swiggy <grievances@swiggy.in>", subject=f"Your case {a_case}", on=D0 + timedelta(days=1), snippet="Ticket created.")
    w["inbox"].messages = [msg, strong]
    got = c.post(f"/tracked-cases/{a_case}/check-replies", headers=w["A"]).json()["new_replies"]
    assert [m["message"]["message_id"] for m in got] == ["<m2@swiggy.in>"] and got[0]["strength"] == "strong"


def test_the_owner_still_gets_sender_only_matches_on_their_own_cases(world, monkeypatch):
    w, c = world, world["c"]
    monkeypatch.setenv("NIVARAN_API_TOKEN", "owner-secret-not-real")
    owner = {"Authorization": "Bearer owner-secret-not-real"}
    own = c.post("/tracked-cases", json={"case": understood().model_dump(mode="json"), "consent": True, "adult": True}, headers=owner).json()["id"]
    w["inbox"].messages = [InboxMessage(message_id="<w1@swiggy.in>", from_addr="Swiggy <grievances@swiggy.in>", subject="Hello", on=D0 + timedelta(days=1), snippet="We got your complaint.")]
    got = c.post(f"/tracked-cases/{own}/check-replies", headers=owner).json()["new_replies"]
    assert len(got) == 1 and got[0]["strength"] == "weak"


def test_tokens_are_checked_and_revocation_is_immediate(world):
    w, c = world, world["c"]
    assert c.get("/tracked-cases").status_code == 401
    assert c.get("/tracked-cases", headers={"Authorization": "Bearer wrong"}).status_code == 401
    assert c.get("/health").status_code == 200
    assert c.get("/tracked-cases", headers=w["A"]).status_code == 200
    assert revoke_user("u1", w["path"]) and not revoke_user("u1", w["path"])
    assert c.get("/tracked-cases", headers=w["A"]).status_code == 401                         # revoked: stops working at once
    assert c.get("/tracked-cases", headers=w["B"]).status_code == 200


def test_the_user_file_never_holds_a_token(world):
    w = world
    raw = w["path"].read_text()
    assert all(t not in raw for t in w["tokens"])
    assert find_user(w["tokens"][0], w["path"]) == "u1" and find_user("not-a-token", w["path"]) is None and find_user("", w["path"]) is None
    assert [u["label"] for u in load_users(w["path"])] == ["Volunteer A", "Volunteer B"]
    with pytest.raises(ValueError):
        add_user("Duplicate", w["path"], user_id="u1")
    assert oct(w["path"].stat().st_mode & 0o777) == "0o600"


def test_speech_to_text_works_for_any_signed_in_person_and_for_nobody_else(world):
    w, c = world, world["c"]
    body = {"audio_b64": base64.b64encode(b"RIFFfake").decode(), "mime_type": "audio/wav"}
    assert c.post("/speech/transcribe", json=body, headers=w["B"]).status_code == 200
    assert c.post("/speech/transcribe", json=body).status_code == 401


def test_with_people_set_up_even_this_computer_needs_a_token(world):
    # localhost is only trusted while no tokens exist at all
    assert TestClient(app, client=("127.0.0.1", 5000)).get("/tracked-cases").status_code == 401
