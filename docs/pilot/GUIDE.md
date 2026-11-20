# Pilot guide (builder's checklist)

Goal: handle **at least 3 real complaints end to end** with consenting adult volunteers, and report the results honestly, including failures.

## Before the first volunteer
1. `bash scripts/run_pilot.sh` on the laptop (same Wi-Fi as the phone). Start the app with the command it prints. Check: open the app, the cases list loads.
2. Put `SMTP_USER` (the Gmail address letters go out from) and `SMTP_PASSWORD` (a Gmail **app password**, never the real password) in `.env`. Without them, letters can be written and approved but not sent.
3. Print or share `docs/pilot/CONSENT.md`. **No signed consent, no case.**
4. Choose volunteers whose company is in the verified directory (`backend/app/directory/companies.json`) and whose complaint is real and current.

## For each case (do it together, volunteer holds the phone)
1. New case: the volunteer says or types the problem once. Check "Is this right?" with them. They accept the privacy notice and confirm they are 18 or older.
2. Read the next step. Write the letter, let the volunteer **read it fully**, edit if they want, approve, then they tap Send.
3. Note the date. Come back on the ladder dates (day 3, 7, 15). Tap "Check my inbox" for replies (only works for the builder's own inbox; for the volunteer's email, ask them to forward replies or tell you).
4. If the ladder reaches the regulator's portal, the volunteer files it themselves with the kit; note the docket number.
5. Close the case as solved or stopped. Fill one row in `docs/pilot/RESULTS.md` the same day.

## Rules
- Never type a volunteer's password, OTP, PIN or card detail anywhere. If they offer one, stop and tell them not to.
- Do not email a company for a volunteer without that volunteer approving the exact text.
- Record failures (wrong contact, no reply, the app broke) with the same care as successes.
- Delete a volunteer's case on request, the same day.

## What counts as "solved"
The volunteer says the company gave what they asked (refund, repair, replacement, cancellation, information) or a fair alternative they accept. A reply that only says "we are looking into it" is **not** solved.
