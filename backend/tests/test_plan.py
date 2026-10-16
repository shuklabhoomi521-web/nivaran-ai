from tests.conftest import case_dict

PLAN = {
    "channel": "call",
    "reason": "A refund is stuck and a phone agent can fix it fast.",
    "opening_line": "Hello, I am calling for a customer about order 4839201, which arrived cold.",
    "proof_to_keep": ["Order confirmation", "Photo of the food"],
}


def _case(**over):
    c = case_dict(**over)
    c.pop("follow_up_question")
    return c


def test_plan_for_company_with_no_phone_line_switches_to_email(client_with):
    client, fake = client_with(PLAN)  # the AI asks for a call; Swiggy officially has no phone line
    r = client.post("/cases/plan", json={"case": _case(company="Swiggy")})
    body = r.json()
    assert r.status_code == 200
    assert body["plan"]["channel"] == "call"          # what the AI wanted
    assert body["channel"] in ("email", "complaint")  # what we will really do
    assert "not possible" in body["channel_note"]
    assert body["contact"]["phone"] is None
    assert "does not have any official customer care phone line" in body["contact"]["no_phone_notice"]
    assert body["can_proceed"] is True
    assert body["contact"]["grievance_email"]["value"] == "grievances@swiggy.in"
    # the AI was told what Swiggy supports
    assert "no_phone_line" in fake.calls[0]["user"] and '"call"' not in fake.calls[0]["user"].split("available_channels")[1].split("]")[0]


def test_plan_for_company_with_a_phone_keeps_the_call_and_gives_the_directory_number(client_with):
    client, _ = client_with(PLAN)
    body = client.post("/cases/plan", json={"case": _case(company="IndiGo", category="airlines")}).json()
    assert body["channel"] == "call" and body["channel_note"] is None
    phone = body["contact"]["phone"]
    assert phone["value"] == "0124-4973838"
    assert phone["source_url"].startswith("https://www.goindigo.in/")
    assert phone["source_quote"]


def test_plan_never_uses_a_number_the_ai_wrote(client_with):
    sneaky = dict(PLAN, opening_line="Please call me on 98765 43210 or use 1800 111 222.")
    client, _ = client_with(sneaky)
    body = client.post("/cases/plan", json={"case": _case(company="IndiGo")}).json()
    assert body["contact"]["phone"]["value"] == "0124-4973838"   # only the directory decides the contact


def test_plan_for_company_not_in_directory_cannot_proceed(client_with):
    client, _ = client_with(PLAN)
    body = client.post("/cases/plan", json={"case": _case(company="Nonexistent Foods Pvt Ltd")}).json()
    assert body["can_proceed"] is False
    assert body["contact"] is None and body["channel"] is None
    assert "not in our verified directory" in body["note"]


def test_plan_for_company_with_empty_directory_entry_cannot_proceed(client_with):
    client, _ = client_with(PLAN)
    body = client.post("/cases/plan", json={"case": _case(company="Indian Railways", category="railways")}).json()
    assert body["can_proceed"] is False
    assert body["contact"]["channels_available"] == []
    assert "needs_check" in " ".join(body["contact"]["warnings"])


def test_plan_matches_company_by_alias_and_spelling(client_with):
    client, _ = client_with(PLAN)
    body = client.post("/cases/plan", json={"case": _case(company="  tangedco ", category="utilities")}).json()
    assert body["contact"]["company"] == "TNEB"


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
    r = client.post("/cases/plan", json={"case": _case(company="IndiGo")})
    assert "4111" not in r.text
