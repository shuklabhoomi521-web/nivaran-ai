# Phase 0 notes

## Summary (5 lines)
- Built: folder structure, FastAPI `/health`, one passing pytest, `.env.example`, CLAUDE.md, docs/PLAN.md, README.
- Built: private GitHub repo `nivaran`, pushed, tagged `phase-0-done`.
- Broke: nothing. Python is 3.12 here (plan says 3.11+, so fine).
- Learned: a company-free phone provider is the biggest open risk (see Research 2).
- Learned: Play Store notification-access rules are not confirmed; plan Layers 3 and 4 as the safe core.

## Research 1 — Play Store rules for reading OTPs
Checked on 2026-10-15. Honest status: **partly confirmed**.
- Confirmed (Google Play SMS/Call Log policy): reading SMS is limited to apps that are the *default* SMS, Phone or Assistant app. "SMS notification enhancement and alerts" is a restricted use. Any permitted use must be declared in Play Console's Permissions Declaration Form. Undeclared use can mean suspension.
- Google's own advice for OTPs: use the **SMS Retriever API** (no extra permission, but it only reads SMS made for your own app's hash, so it does not help with a company's OTP) or let the user type the code.
- **Not confirmed:** I could not find Google's official page for `NotificationListenerService` (notification access). It is a user-granted special access, and I believe Play reviews it as sensitive, but I have no primary source yet.
- What this means for Layer 1 (auto-read from notifications): **risky**. Plan for Layer 3 (one-tap "Share OTP?") and Layer 4 (pause/resume) as the safe core. Treat Layer 1 as optional, and re-check the exact Play policy before Phase 7.
- Sources: https://support.google.com/googleplay/android-developer/answer/9047303 , https://support.google.com/googleplay/android-developer/answer/16909972 , https://support.google.com/googleplay/android-developer/answer/17225965

## Research 2 — Phone-calling providers for an individual (no company)
Checked on 2026-10-15. I did not sign up for anything. Search results are partly from vendor blogs; **verify before relying on them**.

| Option | Works without a company? | Limits / cost (what I found) |
|---|---|---|
| **Twilio (trial, then pay-as-you-go)** | Most likely yes. Its India page lists no outbound document requirements, but the table was garbled. Verify. | Trial: calls only to numbers you verify (max 5), uses a Twilio trial number as caller ID. No Indian number from Twilio per a forum post (unverified). Calls from a +91 caller ID to a +91 number are blocked since 1 Aug 2024, so calls to India come from a foreign number. Twilio says: you need the call recipient's consent for commercial calls; TRAI may block unwanted ones. India per-minute price: not found. |
| **Telnyx** | Unknown. Not found in sources. Ask them in writing. | Pay per minute. Voice API $0.002/min plus the SIP trunk fee. India rate: not found (see their SIP price sheet). |
| **Exotel** (trial) | Trial: yes. Production: **no, probably** — KYC needs a business: company papers, GST or Shop licence, business PAN. Sole proprietor needs GST or Shop & Establishment licence. Individuals are not listed. | Trial has limited outbound minutes, shared numbers only, lower API rate limits. Exact numbers not published. Has a Sarvam integration. Contact hello@exotel.com. |
| Plivo | **No.** India numbers need business registration plus business PAN or GST. | — |

**Suggested path:** build Phases 3-4 against a swappable interface. Test on Twilio trial (calls to your own/friend's verified numbers). In parallel, ask Exotel and Telnyx by email whether an individual or sole proprietor can go live. A **Udyam** (MSME) registration is free and may help you qualify as a sole proprietor; confirm whether Exotel accepts it.

**Legal flag:** AI calls to companies are not the same as marketing calls, but TRAI rules (consent, calling hours, DND) still apply. Ask a lawyer or the provider before Phase 5.

## Email idea added by founder (for Phase 8)
Option B: open the user's own email app with the complaint pre-filled (mailto / share sheet); the user taps Send. Compare with sending from our server using the user's email permission (Gmail OAuth). Decide in Phase 8.

## Decisions logged
- Voice delay (~1.5s) is a goal, not pass/fail.
- Paid-API tests use the `paid_api` marker and do not run by default.
- A call that ends safely without solving the issue counts as "partial", not "solved".
