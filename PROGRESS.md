# Progress

Plan and day-by-day calendar live outside the repo in `~/nivaran-plan` (PLAN.md, CALENDAR.md). This file records what is done, next and blocked.

## Done
- Phases 0-4 (Phase 4 partial: no real phone call). Public repo, CI, README, WRITEUP, REVIEW-BRIEF, release v0.4 with demo videos.
- Outreach: 20 emails 1 Nov, 16 follow-ups and 15 new companies 16 Nov, 4 new companies 18 Nov (see ~/nivaran-outreach/tracker.csv).
- 18 Nov (Day 1): Groq and Gemini keys checked (both work). Phone vendors: MyOperator declined; FreJun says free Teler test credits exist (Sales to say if an individual can verify); Exotel Sales pending.

- 19 Nov (Day 2): Read Teler docs and TRAI summaries: `docs/notes/phone-teler-and-trai.md` (mapping, open questions, rules). Founder created a FreJun account (email code worked; the welcome form crashes with a JavaScript error, dashboard not yet confirmed).

- 19 Nov: `TelerPhone` provider (initiate, DTMF, hang up, allow-list) written from the public docs with 5 tests against a fake server (428 free tests pass). Not tested against the real Teler: FreJun's platform was unreachable (connection reset) and an email is out to their support.

- 19 Nov: read the TRAI Gazette text (scanned, read with OCR): A2P is defined by how the call is started, so our calls count technically; declaration goes through the provider. Wrote `docs/notes/dpdp-basics.md` (core duties from about May 2027; we design to them now).

- 19 Nov: applied to Peakflo (ML Engineer Intern, paid remote) through the YC form with a tailored resume (`resume_peakflo.pdf`). Founder pressed Submit.

- 19 Nov: applied to Lexsi Labs (AI Agent Engineer Intern) via their portal; emailed SuperKalam at join@superkalam.com (the address their YC page invites); Peakflo applied earlier.

- 20 Nov (Day 2): 428 tests pass; public roadmap added at `docs/plan/ROADMAP.md`. FreJun confirmed the account is active and says to reset the password. Twilio line test: our server got Twilio's request and answered 200, yet the call said it could not reach the server; cause still open (read Twilio's error log next). Network matters: the home network blocks Cloudflare's tunnel, a phone hotspot does not. Bhashini needs a supervisor's details, so it is on hold. CallMissed said no.

- 21 Nov (Sprint D1, started late 20 Nov): Twilio line-test finding written down (our reply was valid; the tunnel path is the weak point). Directory v2 started: optional `appellate_authority` and `chat_channels` on companies, plus a verified regulator table by category (`app/directory/regulators.json`: NCH, RBI CMS, IRDAI Bima Bharosa, TRAI, Rail Madad verified with quotes; AirSewa and e-Daakhil marked needs-check, not invented). 434 free tests pass.

## Next
- Day 1 rest: founder makes FreJun Teler, GitHub Student Pack and Bhashini accounts. 19 Nov: tests, TRAI rules, map Teler to the phone layer. 20-22 Nov: phone first, incl. the real test call on your own number (21 Nov).

## Blocked / waiting
- FreJun Sales answer on individual verification; Exotel Sales reply.
- Progress-update emails to all mailed companies wait for the real call result (about 23 Nov).
