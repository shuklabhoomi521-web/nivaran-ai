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

- 21 Nov (Sprint D1 cont.): directory grew to 45 companies (ICICI, PNB, Bank of Baroda, Tata Power-DDL, BESCOM added from official pages with quotes). 10 more planned companies could not be read from their sites (forbidden, moved or empty pages) and were NOT added; list and next steps in `docs/notes/directory-v2.md`. 456 free tests pass.

- 21 Nov: directory now 49 companies (4 more: Canara Bank, ACT Fibernet, IGL, HP Gas). 11 more candidates were unreadable and are listed in `docs/notes/directory-v2.md`. 471 free tests pass.

- 21 Nov (Sprint D3 work done early): case engine built: states, day 0/3/7/15 ladder, next action from the verified directory, JSON store, API, 11 tests (`docs/notes/case-engine.md`). 482 free tests pass.

- 21 Nov: letter writer and send-with-approval built (templates only, no AI; approval hash; directory-only recipients; card/PIN block; fake SMTP tests; `docs/notes/letter-writer.md`). FreJun email asking for a reset link and a sandbox key sent. 492 free tests pass.

- 21 Nov: reply tracking built (read-only inbox, matches replies to cases, hints only, snippet redacted; `docs/notes/reply-tracking.md`). Inbox checked: no new replies from FreJun, Exotel or the internship companies since 20 Nov. 499 free tests pass.

- 21 Nov: portal kits built (steps with exact official quotes or labelled as ours, complaint text, checklist, warnings, needs-check list; `docs/notes/portal-kits.md`). e-Daakhil replaced by e-Jagriti (unverified). 505 free tests pass.

- 21 Nov: mobile app first version built in `mobile/` (Expo SDK 58, TypeScript): cases list, new case, case screen with ladder, letter approve-and-send, portal kit, reply check, delete. Type check clean, 14 jest tests, iOS bundle builds; CI job added. Not run on a real phone yet. FreJun answered: call their support (+91 8035 301 939) for account help.

- 21 Nov: app checked as a web preview (no full Xcode on this Mac, so no iOS simulator): cases list, case screen with ladder and verified contact, letter draft all work against the real backend; demo servers stopped. Outreach: 30 small startups checked, only Hume AI publishes a usable hiring address; emailed. Others print none or only support/sales inboxes.

- 21 Nov: app restyled in liquid glass (native iOS 26 glass, blur fallback, web blur, opaque when Reduce Transparency is on); checked in a browser preview. 17 app tests. Outreach: 2 more emails from Hacker News hiring posts (Namespace, Typify); HN threads are mostly senior or US-only roles, so yield is low.

- 21 Nov (roadmap step 1, privacy and safety): stored cases and drafts encrypted; consent and 18+ gates; retention cleanup with 48 hour warning; red team of 41 messages (4 known gaps listed, not hidden). `docs/notes/privacy-safety.md`. 558 backend tests (+4 expected failures), 18 app tests.

- 21 Nov (roadmap step 2): voice input: `POST /speech/transcribe` (size and type limits, strict redaction, no audio stored) and a Speak button in the new-case screen. Backend tests added; not tried with a real microphone yet.

## Next
- Day 1 rest: founder makes FreJun Teler, GitHub Student Pack and Bhashini accounts. 19 Nov: tests, TRAI rules, map Teler to the phone layer. 20-22 Nov: phone first, incl. the real test call on your own number (21 Nov).

## Blocked / waiting
- FreJun Sales answer on individual verification; Exotel Sales reply.
- Progress-update emails to all mailed companies wait for the real call result (about 23 Nov).
