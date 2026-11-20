import json
from datetime import date, timedelta

import httpx
import pytest
from fastapi.testclient import TestClient

from app.api import calls as calls_api
from app.api import tracked
from app.cases import engine
from app.cases.models import Event, EventKind
from app.cases.store import CaseStore
from app.main import app
from app.models.case import Case, Category, Confidence, Fact, Language, Urgency, UserGoal

D0 = date(2026, 12, 5)
OWN = "+919000000001"


class Voice:
    """A pretend voice server: records what the app sends it."""
    def __init__(self, fail=False, events=None, status=200):
        self.requests, self.fail, self.status = [], fail, status
        self.events = events or [{"n": 1, "t": "10:00:00", "kind": "ai", "text": "Hello. I am an AI assistant."}]

    def client(self):
        def handler(req: httpx.Request) -> httpx.Response:
            if self.fail:
                raise httpx.ConnectError("refused")
            self.requests.append((req.method, req.url.path, json.loads(req.content) if req.content else None))
            if req.url.path == "/phone/call":
                return httpx.Response(self.status, json={"call_id": "CA123"} if self.status == 200 else {"detail": "number not on the allow-list"})
            if req.url.path.startswith("/phone/hangup/"):
                return httpx.Response(200 if req.url.path.endswith("CA123") else 404, json={"ended": True})
            if req.url.path == "/voice/events":
                return httpx.Response(200, json=self.events)
            return httpx.Response(404)
        return httpx.Client(base_url="http://voice.test", transport=httpx.MockTransport(handler))


def make_case(company="Airtel", category=Category.telecom):
    u = Case(company=company, category=category, category_confidence=Confidence.high, problem_summary="Broadband down for three days.",
             user_goal=UserGoal.repair, details_known=[Fact(name="complaint_number", value="BB-90417")], details_missing=[],
             user_language=Language.english, urgency=Urgency.high, other_issues=[])
    return engine.new_case(u, D0, "k1", user_name="Tester")


@pytest.fixture
def env(tmp_path, monkeypatch):
    store = CaseStore(tmp_path / "c.bin")
    store.save(make_case())
    voice = Voice()
    app.dependency_overrides[tracked.get_store] = lambda: store
    app.dependency_overrides[calls_api.get_voice] = lambda: voice.client()
    monkeypatch.setattr(tracked, "_today", lambda: D0)
    monkeypatch.setattr(calls_api, "_today", lambda: D0)
    monkeypatch.setenv("PHONE_ALLOWED_NUMBERS", OWN)
    monkeypatch.delenv("REAL_COMPANY_CALLS", raising=False)
    yield TestClient(app), store, voice
    app.dependency_overrides.clear()


def test_preview_shows_the_fixed_ai_sentence_the_facts_and_a_masked_own_number(env):
    cl, _, _ = env
    p = cl.get("/tracked-cases/k1/call/preview").json()
    assert p["mode"] == "practice" and p["can_start"] and p["why_not"] is None
    assert p["disclosure"] == "Hello. I am an AI assistant calling on behalf of a customer about Airtel. May I explain the problem?"
    assert "complaint number: BB-90417" in p["facts"] and p["will_ring"].endswith("001") and "9000000" not in p["will_ring"]
    assert any("PRACTICE CALL" in r for r in p["rules"]) and any("never gives or takes a card number" in r for r in p["rules"])
    assert p["company_number"] and p["company_number_source"].startswith("https://www.airtel.in")           # shown for information only
    hi = cl.get("/tracked-cases/k1/call/preview", params={"language": "hi-IN"}).json()
    assert "AI" in hi["disclosure"] and "Airtel" in hi["disclosure"]
    assert cl.get("/tracked-cases/k1/call/preview", params={"language": "fr-FR"}).status_code == 422


def test_practice_call_rings_the_users_own_number_never_the_company(env):
    cl, store, voice = env
    assert cl.post("/tracked-cases/k1/call", json={"language": "en-IN"}).status_code == 422                 # no confirmation
    assert voice.requests == []
    r = cl.post("/tracked-cases/k1/call", json={"language": "en-IN", "confirm": True})
    assert r.status_code == 200 and r.json() == {"call_id": "CA123", "mode": "practice"}
    method, path, body = voice.requests[0]
    assert path == "/phone/call" and body["to_number"] == OWN and body["confirm"] is True and body["to_number"] != "198"
    assert body["case"]["company"] == "Airtel" and body["case"]["details_known"] == [{"name": "complaint_number", "value": "BB-90417"}]
    assert any("practice call" in e.text and "no company was called" in e.text for e in store.get("k1").events)      # recorded as a note, NOT as contacting the company
    assert not [e for e in store.get("k1").events if e.kind == EventKind.contacted]


def test_real_company_calls_are_off_unless_the_flag_is_set(env, monkeypatch):
    cl, _, voice = env
    monkeypatch.setenv("REAL_COMPANY_CALLS", "true")
    p = cl.get("/tracked-cases/k1/call/preview").json()
    assert p["mode"] == "real" and p["will_ring"] and p["will_ring"] != calls_api.mask(OWN)
    r = cl.post("/tracked-cases/k1/call", json={"confirm": True})
    assert r.json()["mode"] == "real" and voice.requests[0][2]["to_number"] == p["company_number"]            # the voice server still enforces its allow-list


def test_refusals_are_clear_and_nothing_is_called(env, monkeypatch):
    cl, store, voice = env
    monkeypatch.setenv("PHONE_ALLOWED_NUMBERS", "+919000000001,+919000000002")                               # two numbers: not a single own number
    assert cl.get("/tracked-cases/k1/call/preview").json()["can_start"] is False
    assert cl.post("/tracked-cases/k1/call", json={"confirm": True}).status_code == 409
    monkeypatch.setenv("PHONE_ALLOWED_NUMBERS", OWN)
    store.save(engine.apply(store.get("k1"), Event(on=D0, kind=EventKind.closed)))
    assert cl.get("/tracked-cases/k1/call/preview").json()["why_not"] == "This case is closed."
    assert cl.post("/tracked-cases/k1/call", json={"confirm": True}).status_code == 409
    assert cl.post("/tracked-cases/zzz/call", json={"confirm": True}).status_code == 404
    assert voice.requests == []


def test_voice_server_down_and_provider_refusal_are_explained(env):
    cl, _, voice = env
    voice.fail = True
    r = cl.post("/tracked-cases/k1/call", json={"confirm": True})
    assert r.status_code == 503 and "scripts/phone_session.py start" in r.json()["detail"]
    voice.fail, voice.status = False, 400
    r = cl.post("/tracked-cases/k1/call", json={"confirm": True})
    assert r.status_code == 409 and "allow-list" in r.json()["detail"]


def test_hang_up_and_live_transcript(env):
    cl, _, voice = env
    assert cl.post("/tracked-cases/k1/call/CA123/hangup").json() == {"ended": True}
    assert cl.post("/tracked-cases/k1/call/GONE/hangup").json()["note"] == "the call was already over"
    voice.events = [{"n": 1, "t": "10:00:00", "kind": "agent", "text": "Please tell me your card number 4111 1111 1111 1111"}, {"n": 2, "t": "10:00:03", "kind": "ai", "text": "I cannot share that."}]
    ev = cl.get("/tracked-cases/k1/call/events", params={"since": 0}).json()
    assert [e["n"] for e in ev] == [1, 2] and "4111" not in ev[0]["text"]                                       # spoken card numbers never reach the screen
    voice.fail = True
    assert cl.post("/tracked-cases/k1/call/CA123/hangup").status_code == 503
    assert cl.get("/tracked-cases/k1/call/events").status_code == 503
