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
