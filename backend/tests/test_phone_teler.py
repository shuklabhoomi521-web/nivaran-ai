import asyncio
import json

import httpx
import pytest

from app.channels.phone.teler import PhoneError, TelerPhone


def run(c):
    return asyncio.run(c)


def make(handler):
    return TelerPhone("test-key-not-real", "+910000000001", httpx.AsyncClient(transport=httpx.MockTransport(handler)))


def test_only_allow_listed_numbers_can_be_called(monkeypatch):
    monkeypatch.setenv("PHONE_ALLOWED_NUMBERS", "+919876543210")
    seen = []

    def handler(req):
        seen.append(req)
        return httpx.Response(202, json={"call_id": "cs_01TEST"})
    p = make(handler)
    assert run(p.place_call("98765 43210", "https://x.test/flow", "https://x.test/status")) == "cs_01TEST"
    body = json.loads(seen[0].content)
    assert body == {"from_number": "+910000000001", "to_number": "+919876543210", "flow_url": "https://x.test/flow",
                    "status_callback_url": "https://x.test/status"}
    assert seen[0].headers["X-API-Key"] == "test-key-not-real" and seen[0].url.path.endswith("/calls/initiate")
    with pytest.raises(PhoneError):
        run(p.place_call("+911234567890", "https://x.test/flow"))      # a company or a stranger: refused, nothing sent
    assert len(seen) == 1


def test_no_allow_list_means_no_calls(monkeypatch):
    monkeypatch.delenv("PHONE_ALLOWED_NUMBERS", raising=False)
    with pytest.raises(PhoneError):
        run(make(lambda r: httpx.Response(202, json={"call_id": "x"})).place_call("+919876543210", "https://x.test/flow"))


def test_call_id_is_found_in_either_reply_shape(monkeypatch):
    monkeypatch.setenv("PHONE_ALLOWED_NUMBERS", "+919876543210")
    assert run(make(lambda r: httpx.Response(200, json={"data": {"id": "cs_2"}})).place_call("+919876543210", "https://x.test/f")) == "cs_2"
    with pytest.raises(PhoneError):
        run(make(lambda r: httpx.Response(200, json={})).place_call("+919876543210", "https://x.test/f"))


def test_dtmf_and_hangup_use_idempotency_keys_and_check_digits():
    seen = []

    def handler(req):
        seen.append(req)
        return httpx.Response(202, json={"request_id": "r1"})
    p = make(handler)
    run(p.send_dtmf("cs_1", "1#"))
    run(p.hang_up("cs_1"))
    assert seen[0].url.path.endswith("/calls/cs_1/dtmf") and json.loads(seen[0].content) == {"digits": "1#"}
    assert seen[1].url.path.endswith("/calls/cs_1/hangup")
    assert seen[0].headers["Idempotency-Key"] and seen[1].headers["Idempotency-Key"] and seen[0].headers["Idempotency-Key"] != seen[1].headers["Idempotency-Key"]
    for bad in ("", "12x", "1 2"):
        with pytest.raises(PhoneError):
            run(p.send_dtmf("cs_1", bad))
    assert len(seen) == 2


def test_errors_and_missing_setup_are_clear(monkeypatch):
    monkeypatch.setenv("PHONE_ALLOWED_NUMBERS", "+919876543210")
    with pytest.raises(PhoneError) as e:
        run(make(lambda r: httpx.Response(403, text="number_not_verified")).place_call("+919876543210", "https://x.test/f"))
    assert "403" in str(e.value)
    with pytest.raises(PhoneError):
        run(make(lambda r: httpx.Response(409)).hang_up("cs_1"))
    monkeypatch.delenv("TELER_API_KEY", raising=False)
    with pytest.raises(PhoneError):
        TelerPhone()
