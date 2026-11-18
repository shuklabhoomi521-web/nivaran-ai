"""FreJun Teler phone provider (India). Same safety as Twilio: it only dials numbers on the allow-list (PHONE_ALLOWED_NUMBERS).

Written from the public docs (https://frejun.com/docs/teler/) on 2026-11-19, BEFORE any real call, so three things are unverified:
the exact shape of the "initiate" reply (we accept `call_id`, `id` or the same inside `data`), the Stream call-flow JSON, and whether
sandbox calls to +91 mobiles work. The audio side (WebSocket, 16-bit PCM at 8 kHz) is not here yet. See docs/notes/phone-teler-and-trai.md."""
import os
import uuid

import httpx

from app.channels.phone.base import PhoneProvider
from app.channels.phone.twilio import PhoneError, allowed_numbers, normalise


class TelerPhone(PhoneProvider):
    API = "https://api.frejun.ai/api/v1/voice"

    def __init__(self, api_key: str | None = None, from_number: str | None = None, client: httpx.AsyncClient | None = None):
        self.api_key = api_key or os.getenv("TELER_API_KEY", "").strip()
        self.from_number = from_number or os.getenv("TELER_FROM_NUMBER", "").strip()
        if not (self.api_key and self.from_number):
            raise PhoneError("Teler is not set up: add TELER_API_KEY and TELER_FROM_NUMBER to .env (sandbox: the test key and the sandbox number).")
        self._client = client or httpx.AsyncClient(timeout=20)

    def _headers(self, idempotent: bool = False) -> dict[str, str]:
        h = {"X-API-Key": self.api_key, "Content-Type": "application/json"}
        if idempotent:
            h["Idempotency-Key"] = uuid.uuid4().hex
        return h

    async def place_call(self, to_number: str, webhook_url: str, status_callback_url: str | None = None) -> str:
        """webhook_url is our public https call-flow address. Teler POSTs to it when the phone is answered and expects JSON within 5 s."""
        to = normalise(to_number)
        if to not in allowed_numbers():
            raise PhoneError(f"{to} is not on the allow-list (PHONE_ALLOWED_NUMBERS). We only call numbers the founder has approved.")
        body = {"from_number": self.from_number, "to_number": to, "flow_url": webhook_url}
        if status_callback_url:
            body["status_callback_url"] = status_callback_url
        r = await self._client.post(f"{self.API}/calls/initiate", headers=self._headers(), json=body)
        if r.status_code not in (200, 201, 202):
            raise PhoneError(f"Teler refused the call (HTTP {r.status_code}): {r.text[:160]}")
        j = r.json() if r.content else {}
        cid = j.get("call_id") or j.get("id") or (j.get("data") or {}).get("call_id") or (j.get("data") or {}).get("id")
        if not cid:
            raise PhoneError("Teler accepted the call but sent no call id; check the reply shape in the docs.")
        return str(cid)

    async def send_dtmf(self, call_id: str, digits: str) -> None:
        if not digits or any(c not in "0123456789*#ABCD" for c in digits):
            raise PhoneError("Keypad digits must be 0-9, *, # or A-D.")
        r = await self._client.post(f"{self.API}/calls/{call_id}/dtmf", headers=self._headers(True), json={"digits": digits})
        if r.status_code != 202:
            raise PhoneError(f"Teler could not send the keypad tones (HTTP {r.status_code}).")

    async def hang_up(self, call_id: str) -> None:
        r = await self._client.post(f"{self.API}/calls/{call_id}/hangup", headers=self._headers(True), json={"reason": "user_or_safety_stop"})
        if r.status_code != 202:
            raise PhoneError(f"Teler could not end the call (HTTP {r.status_code}).")
