"""Twilio phone provider (free trial in Phase 4). Calls a number and connects the call audio to our voice bot over a websocket
("Media Streams"). Safety: it only dials numbers on the allow-list (PHONE_ALLOWED_NUMBERS: the friend's verified number in Phase 4)."""
import os
import re
from xml.sax.saxutils import quoteattr

import httpx

from app.channels.phone.base import PhoneProvider


class PhoneError(RuntimeError):
    pass


def normalise(number: str) -> str:
    n = re.sub(r"[\s\-()]", "", number or "")
    return n if n.startswith("+") else "+" + n if re.fullmatch(r"\d{10,15}", n) else n


def allowed_numbers() -> set[str]:
    return {normalise(x) for x in os.getenv("PHONE_ALLOWED_NUMBERS", "").split(",") if x.strip()}


def stream_twiml(ws_url: str, params: dict[str, str]) -> str:
    """The instructions Twilio follows when the call connects: open a websocket to our bot and stream the audio."""
    ps = "".join(f"<Parameter name={quoteattr(k)} value={quoteattr(str(v))}/>" for k, v in params.items())
    return f"<Response><Connect><Stream url={quoteattr(ws_url)}>{ps}</Stream></Connect></Response>"


class TwilioPhone(PhoneProvider):
    API = "https://api.twilio.com/2010-04-01"

    def __init__(self, sid: str | None = None, token: str | None = None, from_number: str | None = None, client: httpx.AsyncClient | None = None):
        self.sid = sid or os.getenv("TWILIO_ACCOUNT_SID", "").strip()
        self.token = token or os.getenv("TWILIO_AUTH_TOKEN", "").strip()
        self.from_number = from_number or os.getenv("TWILIO_FROM_NUMBER", "").strip()
        if not (self.sid and self.token and self.from_number):
            raise PhoneError("Twilio is not set up: add TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN and TWILIO_FROM_NUMBER to .env.")
        self._client = client or httpx.AsyncClient(timeout=20)

    async def place_call(self, to_number: str, webhook_url: str, params: dict[str, str] | None = None) -> str:
        """webhook_url here is the public wss:// address of our bot's websocket."""
        to = normalise(to_number)
        if to not in allowed_numbers():
            raise PhoneError(f"{to} is not on the allow-list (PHONE_ALLOWED_NUMBERS). In Phase 4 we only call the friend's verified number.")
        r = await self._client.post(f"{self.API}/Accounts/{self.sid}/Calls.json", auth=(self.sid, self.token),
                                    data={"To": to, "From": self.from_number, "Twiml": stream_twiml(webhook_url, params or {})})
        if r.status_code not in (200, 201):
            raise PhoneError(f"Twilio refused the call (HTTP {r.status_code}): {r.text[:160]}")
        return r.json()["sid"]

    async def send_dtmf(self, call_id: str, digits: str) -> None:
        raise PhoneError("Keypad tones are played by the voice bot itself (see app/voice/dtmf.py), not through the provider API.")

    async def hang_up(self, call_id: str) -> None:
        r = await self._client.post(f"{self.API}/Accounts/{self.sid}/Calls/{call_id}.json", auth=(self.sid, self.token), data={"Status": "completed"})
        if r.status_code not in (200, 201):
            raise PhoneError(f"Twilio could not end the call (HTTP {r.status_code}).")
