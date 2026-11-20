# Letter writer and send-with-approval (sprint day 4 work, built 2026-11-21)

Code: `backend/app/letters/` (`compose.py`, `outbox.py`) and `backend/app/api/letters.py`. Tests: `backend/tests/test_letters.py` (10 tests, fake mail server).

## Design
- **No AI writes the letter.** Fixed templates filled only with the facts the user gave and the case history (dates, channel, docket numbers). A letter cannot contain an invented fact, law, deadline or threat. A test checks that words such as "legal", "court" and "compensation" never appear.
- Templates per rung: first message, follow-up (quotes the date of the first message), grievance officer escalation (with history), appeal (with history), and a complaint text for the regulator's portal (the user files it by hand; the app never sends portal complaints).
- English only for now. A summary in the user's language is planned.

## Safety rules, all tested
1. **Nothing is sent without the user's approval** of exactly this text. Approving stores a hash; editing after approval cancels it; approved drafts cannot be edited.
2. **The recipient must be an address in the verified directory** for that company (support, grievance officer or appellate email). Any other address is refused even if approved.
3. **Payment data is blocked twice** (when composing and again at send): card numbers, CVV, PIN.
4. A draft is sent at most once. Sending records a `contacted` event on the case, so the ladder moves on.
5. Credentials come only from `.env` (`SMTP_USER`, `SMTP_PASSWORD` as a Gmail app password).

## API
`POST /tracked-cases/{id}/drafts` (compose from the next action), `GET /tracked-cases/{id}/drafts`, `PATCH /drafts/{id}`, `POST /drafts/{id}/approve`, `POST /drafts/{id}/reject`, `POST /drafts/{id}/send`.

## Not yet
Reading replies from the inbox (next), the mobile screens, encrypting the stores.
