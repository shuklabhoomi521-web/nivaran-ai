from tests.conftest import case_dict

PLAN = {
    "channel": "call",
    "reason": "A refund is stuck and a phone agent can fix it fast.",
    "opening_line": "Hello, I am calling for a customer about order 4839201, which arrived cold.",
    "proof_to_keep": ["Order confirmation", "Photo of the food"],
}


def _case():
    c = case_dict()
    c.pop("follow_up_question")
    return c


def test_plan_returns_channel_and_opening_line(client_with):
    client, fake = client_with(PLAN)
    r = client.post("/cases/plan", json={"case": _case()})
    assert r.status_code == 200
    assert r.json()["channel"] == "call"
    assert fake.calls


def test_plan_refuses_when_company_unknown(client_with):
    client, fake = client_with(PLAN)
    c = _case()
    c["company"] = None
    r = client.post("/cases/plan", json={"case": c})
    assert r.status_code == 422
    assert fake.calls == []


def test_plan_card_number_is_scrubbed(client_with):
    bad = dict(PLAN, proof_to_keep=["Card 4111 1111 1111 1111 statement"])
    client, _ = client_with(bad)
    r = client.post("/cases/plan", json={"case": _case()})
    assert "4111" not in r.text
