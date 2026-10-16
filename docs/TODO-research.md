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
