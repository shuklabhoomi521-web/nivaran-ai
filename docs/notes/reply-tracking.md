# Reply tracking (sprint day 5 work, built 2026-11-21)

Code: `backend/app/replies/` (`matcher.py`, `inbox.py`) and `backend/app/api/replies.py`. Tests: `backend/tests/test_replies.py` (7 tests, fake inbox).

## What it does
`POST /tracked-cases/{id}/check-replies` reads the user's inbox, finds replies to a case and adds them to the case timeline as `reply_received` events.

- **Matching:** strong = the email answers a letter we sent (Message-ID) or contains the case reference printed in our letters; weak = the sender is a verified directory address or an official company domain, dated on or after the case started. Strangers never match.
- **Hints, not decisions:** each match says whether it is an automatic acknowledgement (ticket created, we received your message) and whether it *looks* resolved (refund processed, resolved). The user decides; a reply never changes the case state. A ticket or docket number is picked up when one is written.
- **Privacy:** only a short snippet (240 characters) is kept, with card numbers, CVV and PIN removed; never the whole email. The same email is never added twice (`source_id`).

## Read-only guarantee (tested)
The inbox is opened with `readonly=True` and every message is fetched with `BODY.PEEK`, so nothing is marked read, moved, deleted or sent. A test checks that no store, copy, delete or expunge command is ever issued. Credentials: `SMTP_USER` and `SMTP_PASSWORD` (a Gmail app password) in `.env`.

## Not yet
Telling the user in the app when a reply arrives (needs the mobile app), and reading replies for portal complaints (the user pastes the docket number as a note).
