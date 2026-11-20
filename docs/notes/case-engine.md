# Case engine (sprint day 3 work, built 2026-11-21)

Code: `backend/app/cases/` (models, engine, store) and `backend/app/api/tracked.py`. Tests: `backend/tests/test_case_engine.py`.

## What it does
- A **tracked case** is the case file that lives for days: facts the user gave, state, and an append-only timeline of events.
- States: new, waiting (we contacted the company), escalated (we went above the first line), resolved, closed.
- **Ladder (defaults chosen by us, not legal advice):** day 0 first contact, day 3 follow-up, day 7 grievance officer, day 15 appellate authority, or the regulator's portal when the directory has no appellate authority.
- `next_action` returns the one thing to do next with its target taken **only from the verified directory** (email, phone or portal link, plus the official page and the exact quote). If a rung has no verified target it moves up (ending at the regulator) and says so. If a company lists no support contact (Swiggy), the official grievance address is the first contact and the note says why.
- Rules enforced: a closed or solved case accepts no more events; no event older than the case; every contact names its rung; a step cannot be repeated or skipped back to.
- Storage: one JSON file (`.cases.json`, git-ignored, holds private details; must be encrypted before real users). Delete-my-data is `DELETE /tracked-cases/{id}`.

## API
`POST /tracked-cases`, `GET /tracked-cases`, `GET /tracked-cases/{id}`, `POST /tracked-cases/{id}/events`, `GET /tracked-cases/{id}/next` (action plus the whole ladder with done/due/upcoming), `DELETE /tracked-cases/{id}`.

## Not yet
The letter writer and send-with-approval (next), reply tracking from the inbox, reminders in the mobile app, encryption of the store.
