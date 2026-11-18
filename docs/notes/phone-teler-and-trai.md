# Phone route: FreJun Teler and TRAI rules (checked 2026-11-19)

Status: reading only. No Teler account has been used yet and no code is written. Sources are public docs and news; the TRAI Gazette PDF is a scanned image and could not be read by tool, so the rules below are **not verified from the primary text**.

## What FreJun told us (support emails, 2026-11-17)
- Free test credits exist and Teler can be tested independently.
- Whether an individual (no company) can verify for real calls is **open**: their Sales team will answer.

## How Teler would plug into our phone layer
Our interface is `PhoneProvider` in `backend/app/channels/phone/base.py` (place_call, send_dtmf, hang_up).

| Our call | Teler | Notes |
|---|---|---|
| `place_call(to, webhook_url)` | `POST https://api.frejun.ai/api/v1/voice/calls/initiate` with `from_number`, `to_number`, `flow_url`, `status_callback_url` | Header `X-API-Key`. Sandbox: test key, sandbox from-number, **verified** to-number. |
| `send_dtmf(call_id, digits)` | `POST /api/v1/voice/calls/{call_id}/dtmf` (`digits` 0-9*#A-D, `duration_ms` 40-1000) | `Idempotency-Key` header required. Only for Voice App calls. Returns 202 (queued, not confirmed). |
| `hang_up(call_id)` | `POST /api/v1/voice/calls/{call_id}/hangup` | Same headers. Call id looks like `cs_<ULID>`. |
| Audio in and out | Teler opens a WebSocket to our `ws_url`. First message `start`, then `audio` messages with base64 **16-bit linear PCM, 8000 Hz, mono**, 400 ms chunks by default | Twilio sends mu-law. We need a new serializer (no mu-law step). Our low-pass filter before downsampling still applies. |
| Barge-in | We send `interrupt` (with `chunk_id`) or `clear` | Maps to our interruption handling. |
| Call flow | Teler first calls `POST /flow` on our public HTTPS server and expects JSON within **5 seconds** | Same Cloudflare tunnel idea as Twilio. A slow answer drops the call. |

Teler also lists recipes for Sarvam, Gemini Live and LiveKit, so our Sarvam speech choice fits.

## Open questions (ask FreJun Sales or read the dashboard)
1. Can an individual verify for live calls, or is a company needed?
2. Do sandbox calls work to **+91 mobiles**? The docs do not say.
3. Is media streaming allowed in sandbox? The docs do not say.
4. How many credits, and how long does the sandbox last?

## Sandbox steps (from docs)
Dashboard in sandbox mode, Developers, Verified numbers, enter your own mobile, Teler calls it and plays an OTP, you enter it.

## TRAI Third Amendment (notified 18 Sep 2026), what is known
- A2P (software-started) calls must be declared in advance with the CLI ranges, to the originating operator. Undeclared A2P calls are treated as unsolicited commercial communication (spam). Source: FoxMandal summary.
- Most rules start 30 days after Gazette publication. The A2P declaration and the A2P charge start **after 60 days**, which is about now (mid to late November 2026).
- Terminating operator may charge up to Rs 0.05 per minute for A2P calls, with exemptions.
- **Unknown:** the text I could read does not say whether a consumer-side assistant calling customer care is covered, or whether the rule is only for commercial calls. Treat it as unclear. Not legal advice. Next step: ask FreJun/Exotel how they treat it, and read the Gazette text with OCR.

## Decision still to make (22 Nov)
Which provider, how a student goes live (KYC), and the TRAI declaration. Until then: test only to your own verified number, never to a real company.
