# Call for me (sprint work, built 2026-11-21)

Code: `backend/app/api/calls.py`, `mobile/src/screens/CallScreen.tsx`. Tests: `backend/tests/test_calls_api.py` (6), app API tests.

## What it is
A screen where the user starts a phone call by Nivaran. The backend (token protected) forwards to the local voice server from Phase 4 (`app/voice/server.py`), so the same call brain, AI-disclosure sentence, keypad menus, hold handling and encrypted transcripts are used.

## Safety rules (tested)
- **Practice mode is the default.** Nivaran rings the user's own number (exactly one number in `PHONE_ALLOWED_NUMBERS`) and the user plays the company. **No real company is called.** The practice call is recorded on the case as a note, never as contacting the company.
- **Real company calls are off** unless `REAL_COMPANY_CALLS=true`. Even then the voice server only dials numbers on its allow-list, so a company number is refused unless the founder adds it. Phase 5 has not started; the founder approves each real call.
- The user must tick a consent box and confirm each call. The screen first shows the exact first sentence the AI will say (fixed text in 4 languages, never written by the AI), the only facts it may use, and the rules.
- Hang up is always on screen. Spoken card numbers and PINs are removed before the transcript reaches the screen.
- If the voice server is not running the app says so and how to start it.

## Not working yet (honest)
- A real call needs the voice server, a tunnel the network allows, and a working phone provider. On 19 Nov the Twilio line test reached our server but the call said it could not reach it; FreJun access is still being fixed. So **no call has been placed from this screen**; it is tested with a pretend voice server.
- "What happened?" after a real company call (record the outcome and move to the next step) is the normal case screen: use "I did this step myself" or the ladder.
