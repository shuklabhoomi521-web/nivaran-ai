# Research to do before later phases

## Before Phase 5 (real company calls): TRAI rules
Research and write down, with official sources (trai.gov.in, not vendor blogs):
- Are AI-assisted calls to company helplines covered by the TCCCPR (telemarketing) rules? Which parts apply?
- Calling hours, DND scrubbing, number series, caller ID rules, call recording consent.
- Whether the provider (Twilio / Exotel / Telnyx) needs us to register anything.
- If unclear, ask the provider in writing, or a lawyer.

## Phone provider
- Phase 4: Twilio trial, calls to the founder's friend's verified number only.
- Phase 5: waiting for Exotel's answer on KYC with Udyam registration (founder emailed them).
- Phone code stays behind `backend/app/channels/phone/base.py` so providers can be swapped.

## Before Phase 7
- Re-check the Google Play policy for notification access (not confirmed in Phase 0).

## Phase 9: bigger test set
- The 30-problem set is small and mostly written by us. In Phase 9, build a much bigger one (100+ problems, real anonymised cases, more languages and messy spellings).
- Run each problem several times, because the same prompt can give a different answer on a different run (seen in Phase 1: `f-04` flipped between runs).
- Use it to compare our own models against Gemini (`docs/baseline-phase1.md` is the Phase 1 starting point).

## Supabase (skipped for now, founder's decision)
- The company directory lives in `backend/app/directory/companies.json` until Phase 6. No Supabase table or seed script yet.
- Revisit at Phase 6 (mobile app needs login and a shared database).

## Phase 9: run-to-run drift and meaning check
- Same prompt and model gave different answers on different runs (see `docs/baseline-history.md`). Score each problem 3-5 times and report mean and spread.
- The meaning-based fact check is a cheap word-overlap test (lenient). Add a stronger judge (a small model or careful rules) and compare.

## Exotel KYC (founder emailed 2026-10-15/16)
- The founder emailed hello@exotel.com asking whether an individual with a free Udyam registration (sole proprietor) can complete KYC and make outbound calls.
- Waiting for the reply. Needed before Phase 5 (real company calls). Phase 4 uses the Twilio trial. Record Exotel's answer here (documents, time to approve, trial limits).

## Before Phase 5: the contact picker must understand problem types
- Today the picker takes the first suitable phone for a company. It does not look at the problem.
- Needed: contacts get an `applies_to` field (for example BSNL broadband vs mobile vs landline, Jio Fiber vs Jio Mobile, Airtel prepaid vs DTH, Star Health claims vs renewals), and the picker chooses by the case's category / problem type.
- Then test with a live plan call (the plan endpoint has only been tested with a fake AI so far).

## Phase 3.5: add Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati, Punjabi (founder's decision: AFTER Phase 3 is done)
- Order: text brain first (cheap), speech second.
- Text brain: write 3 test problems per language (21 total, plus the usual traps: missing details, two problems in one message, unclear company, card number). The founder gets native speakers from college to check the sentences before we trust the scores. Run the understand endpoint on them, score with the Phase 1 rules, add per-language rows to the baseline table.
- Speech: computer-voice round trip first (free), then real voices: Google FLEURS has te_in, kn_in, ml_in, bn_in, mr_in, gu_in, pa_in dev files (ask before each download; sizes listed on the dataset page) and native speakers can record the same sentences. Check phone quality (8 kHz) like Phase 3.
- Only languages that score well get listed as "supported". Company-side calls stay English/Hindi unless a company needs more.
- Note: Language values already exist in the case model (telugu, kannada, malayalam, bengali, marathi, gujarati, punjabi), so no model change is needed.

## Before Phase 3 is done: new-clips test (founder records 5 NEW clips)
- See `docs/speech-settings-frozen.md`. Settings were tuned on the scored clips, so Sarvam's scores are optimistic until this test.

## Voice recordings in git history (needs the founder's decision)
- The founder's 10 raw .aac recordings were committed once (commit 9dec69a) and are still in the history on the private GitHub repo, although the files are no longer tracked. A purge needs a history rewrite and force-push. See the notes in the Phase 3 discussion.
