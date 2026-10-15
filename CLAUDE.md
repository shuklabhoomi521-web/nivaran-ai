# Nivaran — project guide for Claude

**Current phase: 0 done. Waiting for founder OK to start Phase 1.**

Founder: ECE student. Explain in simple words, short sentences. One line for each hard term.
Full plan: `docs/PLAN.md` (the master prompt). Follow it.

## What Nivaran is
One app that handles any company's customer care for the user. User states the problem once, in their language. The app finds the official contact, calls or emails, and escalates until solved.

## Stack
Python 3.11+, FastAPI, Pydantic · Supabase (Postgres, auth) · Anthropic Claude API · Pipecat voice pipeline ·
Indian speech provider (e.g. Sarvam) and phone provider (Exotel/Plivo/other) behind swappable interfaces ·
React Native + Expo (TypeScript) · PyTorch + Hugging Face (MuRIL/IndicBERT) · pytest, Jest.
Check current docs before using any library or API.

## How we work
1. One phase at a time. Never start the next phase until the founder says so.
2. Plan first; wait for OK.
3. Small steps; run tests after each; show results.
4. Tests for everything. Paid-API tests carry the `paid_api` marker and run only on request (`pytest -m paid_api`).
5. Explain new concepts in one simple line.
6. Secrets only in `.env`. Never in code, logs, or git.
7. Git/GitHub handled by Claude: clean commits, push after each working step, tag `phase-N-done`, private repo `nivaran`. Never force-push, never delete the repo.
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
```
source .venv/bin/activate
cd backend && uvicorn app.main:app --reload
cd backend && python -m pytest
```
