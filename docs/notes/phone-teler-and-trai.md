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

## TRAI Third Amendment (05 of 2026, notified 18 Sep 2026): read from the primary text on 2026-11-19
Source: TRAI Gazette notification PDF (a scanned image, read with macOS text recognition, so small typos are possible). Not legal advice.
- **Definition (new clause ea):** an A2P call is "a voice call that is initiated by an application, software system, or automated platform without direct human dialling and delivered to an individual telecom subscriber", including autodialling, robo-calls and pre-recorded artificial voice.
- **TRAI's own reasoning:** the definition is "based on technical aspects of the call generation", not on the content. TRAI refused to exclude calls with a live human agent, because operators cannot tell them apart. So a call started by our software **is an A2P call by definition**, even if it is not commercial.
- **Declaration (regulation 4):** every "Sender" must declare A2P use to its Originating Access Provider (the telecom operator that carries the call), in advance, with the CLI (caller number) ranges. A call without a declaration "shall be treated as Unsolicited commercial communication". So the practical gate is the operator or provider: they will ask for the declaration.
- **Charge (regulation 35A):** the receiving operator may charge the originating operator up to Rs 0.05 per minute for A2P calls, with no charge for calls from the designated commercial series (140xx, 1600xx, 1601xx) or from the Authority.
- **Start date:** most rules 30 days after Gazette publication. Regulations 4, 6, 8(a) and 18 (declaration, VNO interface, charge) after **60 days**, others after 90. The Gazette publication date is not in the PDF. If it was published on 18 Sep, the declaration rule starts about 17 Nov 2026, so it is in force or about to be.
- **What it does not say:** nothing in the text mentions a consumer's assistant calling a company's customer care, and the purpose is stopping unsolicited commercial calls. Whether a complaint call on a user's behalf is a "Sender" duty is still a question for the provider's compliance team or a lawyer. Plain reading: technically A2P, not commercial in content, but providers will apply the A2P process to every software-started call.
- **What this means for us:** expect the provider to require business verification and a declaration of the caller number before calls to real companies. That is why FreJun and Plivo ask for verified businesses. A sandbox test to our own number is a different thing. Do not claim in the README that Nivaran is "TRAI compliant".

## Decision still to make (22 Nov)
Which provider, how a student goes live (KYC), and the TRAI declaration. Until then: test only to your own verified number, never to a real company.

## Twilio line test, 2026-11-19 on a phone hotspot (finding)
- Twilio placed the call, the phone rang, the trial message played, then Twilio said it could not reach the server. Twilio reported status completed, 9 s.
- Our server DID receive Twilio's request (`POST /phone/twiml`, logged 200 OK). Tested locally afterwards: the reply is valid TwiML, 103 bytes, text/xml, for both POST and GET.
- Conclusion: our code is right. The reply did not make it back to Twilio in time, so the weak point is the tunnel or the network (the home network also blocks Cloudflare entirely; the hotspot worked for the tunnel check but not reliably for the reply).
- Twilio's debugger and Voice Insights are not available on a trial account through the API (error 20003), so the exact Twilio-side error code is only visible in the web console debugger.
- Next experiment (needs a call, so only when the founder says go): before calling, send 20 test requests through the tunnel and check each answers fast; then place the line test again on the steadiest connection.
