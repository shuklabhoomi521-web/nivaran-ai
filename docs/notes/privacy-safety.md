# Privacy and safety pass (sprint work, 2026-11-21)

Follows `docs/notes/dpdp-basics.md`. Not legal advice.

## Done and tested
| Rule | What was built | Tests |
|---|---|---|
| Encrypt private details at rest | Cases and drafts are stored in encrypted files (`backend/app/cases/vault.py`, Fernet). Key from `DATA_ENCRYPTION_KEY` or a git-ignored `.data_key` (permissions 600). An old plain file is read once, then rewritten encrypted. A wrong key is an error, never silent data loss | `tests/test_vault.py` (5) |
| Plain-language notice and consent | `GET /tracked-cases/consent-notice` (versioned text). A case cannot be created without consent; the version and date are stored | `tests/test_case_engine.py` |
| 18 or older | A case cannot be created without the user confirming it; nothing is stored for any refusal | same |
| Delete my data | `DELETE /tracked-cases/{id}` and a button in the app | existing API tests |
| Inactivity cleanup | `app/cases/retention.py` + `scripts/purge_inactive.py`: warn after a year, delete only after a 48 hour warning and only if nothing happened since. The app shows a banner on a warned case | `tests/test_retention.py` (3) |
| No payment data in letters | Card, CVV and PIN are blocked when composing, when building a portal kit, and again at send time. Digits in other scripts (Devanagari, Arabic-Indic, full-width) and dotted card numbers are read first | `tests/test_redteam_letters.py` |

## Red team (`tests/test_redteam_letters.py`)
- 31 attacks that must be blocked (card numbers in many layouts, CVV, UPI PIN, ATM PIN, mixed in long texts, other scripts, dotted, one digit at a time): all blocked.
- 10 ordinary details that must still work (order ids, phone numbers, amounts, dates, ticket numbers): all work.
- Known false positive, kept on purpose: "pin code 603203" looks like a PIN and is blocked. The user can write "postal code".
- **Known gaps, not caught yet (4, marked as expected failures so a future fix shows up):** payment data written as words ("four one one one ..."), "cvv is one two three", numbers split by letters or symbols such as `4111 x 1111 x 1111 x 1111`, and a PIN written in words.

## Not done yet (honest list)
- The AI services in this test version (Groq, Gemini free tier) can read what the user types. Before real users: a paid or self-hosted route (see `CLAUDE.md`).
- Inbox access uses the Gmail app password in `.env`; there is no per-user login yet.
- The case file is one file on one laptop; hosting and a proper database come later.
- No breach plan page yet (one page: who, how, what to say, 72 hours for the Board), and no privacy contact page.
- Transcripts of phone calls already used their own encrypted store (Phase 4).
