from tests.conftest import case_dict


def test_understand_returns_case(client_with):
    client, fake = client_with(case_dict())
    r = client.post("/cases/understand", json={"message": "My Swiggy order came cold. Order 4839201."})
    assert r.status_code == 200
    body = r.json()
    assert body["case"]["company"] == "Swiggy"
    assert body["case"]["user_goal"] == "refund"
    assert body["follow_up_question"] is None
    assert body["redacted"] == []
    assert len(fake.calls) == 1


def test_missing_details_come_back_with_one_question(client_with):
    client, _ = client_with(case_dict(
        company=None, details_known=[], details_missing=["company"],
        follow_up_question="Which company is this about?"))
    body = client.post("/cases/understand", json={"message": "my phone is broken"}).json()
    assert body["case"]["company"] is None
    assert body["follow_up_question"] == "Which company is this about?"


def test_card_number_never_reaches_the_ai_or_the_case(client_with):
    answer = case_dict(
        problem_summary="Paid with card 4111 1111 1111 1111; order failed.",
        details_known=[{"name": "card", "value": "4111111111111111"}])
    client, fake = client_with(answer)
    r = client.post("/cases/understand",
                    json={"message": "paid with card 4111 1111 1111 1111, order failed"})
    assert r.status_code == 200
    sent = fake.calls[0]["user"]
    assert "4111" not in sent and "[CARD NUMBER REMOVED]" in sent
    # even if the AI wrongly copies it, the guard cleans the answer
    assert "4111" not in r.text
    assert "card_number" in r.json()["redacted"]


def test_empty_message_is_rejected(client_with):
    client, fake = client_with(case_dict())
    assert client.post("/cases/understand", json={"message": "   "}).status_code == 422
    assert fake.calls == []


def test_bad_ai_answer_is_an_error_not_a_guess(client_with):
    client, _ = client_with({"company": "Swiggy"})  # missing fields
    r = client.post("/cases/understand", json={"message": "hello"})
    assert r.status_code == 502


def test_schema_sent_to_ai_forbids_extra_fields(client_with):
    client, fake = client_with(case_dict())
    client.post("/cases/understand", json={"message": "x problem"})
    schema = fake.calls[0]["schema"]
    assert schema["additionalProperties"] is False


def test_low_confidence_is_returned_with_a_question(client_with):
    client, fake = client_with(case_dict(
        company=None, category="other", category_confidence="low", details_known=[], details_missing=["company"],
        follow_up_question="Which kind of ticket is this?"))
    body = client.post("/cases/understand", json={"message": "ticket cancel panniten"}).json()
    assert body["case"]["category_confidence"] == "low"
    assert body["follow_up_question"]
    assert "category_confidence" in fake.calls[0]["schema"]["properties"]
