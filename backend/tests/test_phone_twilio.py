import asyncio

import httpx
import pytest

from app.channels.phone.twilio import PhoneError, TwilioPhone, normalise, stream_twiml


def run(c):
    return asyncio.run(c)


def make(handler):
    return TwilioPhone("ACtest", "token-not-real", "+15005550006", httpx.AsyncClient(transport=httpx.MockTransport(handler)))


def test_normalise_numbers():
    assert normalise("+91 98765-43210") == "+919876543210" and normalise("919876543210") == "+919876543210"
    assert normalise("98765 43210") == "+919876543210"          # a 10-digit Indian mobile number gets +91


def test_twiml_streams_the_call_to_our_websocket_and_escapes_values():
    x = stream_twiml("wss://example.test/phone/ws", {"case": 'a"b<c'})
    assert "<Stream" in x and 'url="wss://example.test/phone/ws"' in x and "<c" not in x.replace("&lt;", "")


def test_only_allow_listed_numbers_can_be_called(monkeypatch):
    monkeypatch.setenv("PHONE_ALLOWED_NUMBERS", "+919876543210")
    seen = []

    def handler(req):
        seen.append(req)
        return httpx.Response(201, json={"sid": "CA123"})
    p = make(handler)
    assert run(p.place_call("+91 98765 43210", "https://x.test/phone/twiml?case_id=abc")) == "CA123"
    body = seen[0].content.decode()
    assert "Url=https" in body and "Twiml" not in body            # trial accounts: Twilio fetches the instructions from our server
    with pytest.raises(PhoneError):
        run(p.place_call("+911234567890", "wss://x.test/ws"))      # a real company or any stranger: refused, nothing sent
    assert len(seen) == 1


def test_no_allow_list_means_no_calls(monkeypatch):
    monkeypatch.delenv("PHONE_ALLOWED_NUMBERS", raising=False)
    with pytest.raises(PhoneError):
        run(make(lambda r: httpx.Response(201, json={"sid": "x"})).place_call("+919876543210", "wss://x.test/ws"))


def test_twilio_errors_and_missing_setup_are_clear(monkeypatch):
    monkeypatch.setenv("PHONE_ALLOWED_NUMBERS", "+919876543210")
    with pytest.raises(PhoneError, match="refused"):
        run(make(lambda r: httpx.Response(400, text="bad")).place_call("+919876543210", "wss://x.test/ws"))
    monkeypatch.delenv("TWILIO_ACCOUNT_SID", raising=False)
    with pytest.raises(PhoneError, match="not set up"):
        TwilioPhone()


def test_hang_up_ends_the_call():
    seen = {}

    def handler(req):
        seen["body"] = req.content.decode()
        return httpx.Response(200, json={})
    run(make(handler).hang_up("CA123"))
    assert "Status=completed" in seen["body"]
