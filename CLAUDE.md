# Nivaran — project guide for Claude

**Current phase: 4 DONE AS PARTIAL (tag phase-4-done, founder's choice 2026-10-28): phone layer, call brain and browser practice mode built, 9 of 10 practice calls handled well; the REAL Twilio phone call is still missing (docs/notes/phase-4.md, docs/FOUNDER-TODO.md). Next: Phase 5 only when the founder says so. Phases 0-3 tagged done.**

Founder: ECE student. Explain in simple words, short sentences. One line for each hard term.
Full plan: `docs/PLAN.md` (the master prompt). Follow it. New here? Read `docs/REVIEW-BRIEF.md` first.

## What Nivaran is
One app that handles any company's customer care for the user. User states the problem once, in their language. The app finds the official contact, calls or emails, and escalates until solved.

## Stack
Python 3.11+, FastAPI, Pydantic · Supabase (Postgres, auth) ·
AI brain now: Groq free tier for the live voice (`LLM_PROVIDER=groq`, gpt-oss-120b) with Gemini as automatic backup; Gemini alone for the text chat/tests (`LLM_PROVIDER=gemini`). Claude is optional (`LLM_PROVIDER=anthropic`).
AI brain later: our own fine-tuned open-source models (Phase 9), swapped in one job at a time; Gemini stays as backup until each scores close enough.
Pipecat voice pipeline · Speech: Sarvam AI hears (always auto-detects the language so users can switch); voices per language in `TTS_BY_LANGUAGE` (English Gemini, others Sarvam); Gemini is the free automatic backup (Rs 100 Sarvam credit, then paid); both behind `app/speech/` interfaces; credit tracked in `.sarvam_credits.json` ·
Phone: Twilio trial (Phase 4), Exotel with KYC (Phase 5), behind `channels/phone/base.py` ·
React Native + Expo (TypeScript) · PyTorch + Hugging Face (MuRIL/IndicBERT) · pytest, Jest.
The founder does not want to pay for any API. Prefer free tiers. Check current docs before using any library or API.
Gemini free tier: Google may use free-tier prompts to improve its products. Use only test data there. Never send real users' private data through the free tier (decide on paid tier or own models before real users, Phase 10).
Tests that call the real LLM carry the `live_api` marker and run only on request (`pytest -m live_api`).

## How we work
1. One phase at a time. Never start the next phase until the founder says so.
2. Plan first; wait for OK.
3. Small steps; run tests after each; show results.
4. Tests for everything. Tests that call the real LLM carry the `live_api` marker and run only on request (`pytest -m live_api`).
5. Explain new concepts in one simple line.
6. Secrets only in `.env`. Never in code, logs, or git.
7. Git/GitHub handled by Claude: clean commits, push after each working step, tag `phase-N-done`. Public repo: `shuklabhoomi521-web/nivaran-ai` (the older repo `nivaran` stays private and is not used). Never force-push or delete a repo without asking the founder first.
8. End of phase: check each "Done when" (done/partly/missing + proof), list 3 weakest parts, write `docs/notes/phase-N.md`, suggest a 30s demo clip, update this file, commit, tag, push, STOP.
9. Ask the founder only for: account sign-ups and keys, payment/KYC, phone permissions, OK before each real company call.
10. Design for the future, build for now.
11. Report results honestly. Partial is "partial", not "solved".

## Safety rules (never break)
- Never share, store in plain text, or speak: UPI PIN, card number, CVV, passwords, or any payment-approving OTP. Hard block in the safety guard, with trick tests.
- Contacts only from the verified directory (official source link + "checked on" date). Never from web search.
- Every call starts with the AI saying it is an AI assistant calling on behalf of the user. Never pretend to be the user.
- User approves every email before sending.
- Private user details stored encrypted.
- User can stop any call or action at any time.
- Reading emails/SMS/apps is read-only. Never buy, pay, cancel or change anything. Show findings, wait for yes.

## Run
Needs Python 3.12. The free tests need no keys.
```
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend && python -m pytest -q            # 418 pass, 5 skipped, 30 live_api deselected
cd backend && python -m app.voice.server     # voice bot: http://localhost:7861/voice (needs GROQ_API_KEY, GEMINI_API_KEY in .env)
cd backend && uvicorn app.main:app           # text chat: http://127.0.0.1:8000/chat
python scripts/phone_session.py check        # phone test tunnel (only when the founder asks for a call)
```
Keys go only in `.env` (copy `.env.example`). Read `README.md` (status, results), `docs/WRITEUP.md`, `docs/notes/phase-*.md` and `docs/FOUNDER-TODO.md` first.
Open items: the real Twilio call (Phase 4 partial); Phase 5 only when the founder says so.
