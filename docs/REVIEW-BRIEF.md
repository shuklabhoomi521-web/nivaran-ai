# Review brief: start here if you are new (a person or a new Claude)

**Nivaran** is an AI customer-care agent for India. The user states a problem once, in any language. The agent finds the official contact in a verified directory, then calls or emails for them. Read `README.md` (status and real results) and `docs/WRITEUP.md` (2 pages) first.

## Where things stand (2026-10-29)
- Phases 0-3 done. Phase 1 is partial (28/30 on a strict full re-run). **Phase 4 is partial:** the phone layer and call brain work and were tested with simulated phone-quality audio (9 of 10 practice calls good), but the **real Twilio call never completed** (two answered calls ended after 3-6 s without opening the audio stream; cause not found). **No real company has been called.**
- Phase 5+ has NOT started. Start it only when the founder says so.
- Tags `phase-0-done` ... `phase-4-done`. CI (GitHub Actions) runs the free tests on every push.

## Run it (free, no keys)
```
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend && python -m pytest -q          # 418 pass, 5 skipped, 30 live_api deselected
```
Voice bot: copy `.env.example` to `.env`, add `GROQ_API_KEY` and `GEMINI_API_KEY` (both free), then `cd backend && python -m app.voice.server` and open `http://localhost:7861/voice` in Chrome. Phone practice (you play the company): `/phone/browser`.

## Map
- `backend/app/voice/` bots (`voice_bot.py` browser, `phone_bot.py` phone, `browser_call.py` practice), `call_conversation.py` (the call brain), `server.py` (all routes; the `__main__` block must stay last, a test guards it).
- `backend/app/brain/` AI calls (Groq main, Gemini backup). `backend/app/speech/` hearing and voices behind one interface. `backend/app/directory/` verified companies. `backend/app/safety/` secret redaction. `backend/app/channels/phone/` Twilio.
- `scripts/` evaluation and demo scripts. `experiments/` one-off research. `docs/results/` every measured result. `docs/notes/phase-N.md` what each phase built and learned.

## Rules that must not break
1. Never print or commit secrets. Keys only in `.env` (git-ignored). A test fails if a tracked file has a local absolute path.
2. Contacts only from the verified directory (official source and quote). Never from web search.
3. Every call starts with the fixed AI disclosure. Never speak, ask for or accept an OTP, PIN, card number, CVV or password. These checks are in code.
4. Real calls only to the number in `PHONE_ALLOWED_NUMBERS`, only when the founder asks, with the tunnel closed right after.
5. Report honestly: "partial" stays "partial". Do not change a test rule after seeing the result without saying so.

## Open items (also in `docs/FOUNDER-TODO.md`)
- The real Twilio call: run `python scripts/phone_session.py check`, then a line test (`call --say`), then the call, then `report`. Needs a network that holds a Cloudflare tunnel.
- Speed goal missed: 2-4 s per answer against 1.5 s. Hindi hearing needs the slow free local model or paid Sarvam (credit about Rs 22; Sarvam pauses below Rs 15).
- Phase 5 needs KYC with a phone provider and TRAI-rule research (`docs/TODO-research.md`).
- Demo video links for the README (the founder supplies them).
