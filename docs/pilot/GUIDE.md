# Pilot guide (builder's checklist)

Goal: handle **at least 3 real complaints end to end** with consenting adult volunteers, and report the results honestly, including failures.

## Before the first volunteer
1. `bash scripts/run_pilot.sh` on the laptop (same Wi-Fi as the phone). Start the app with the command it prints. Check: open the app, the cases list loads.
2. Put `SMTP_USER` (the Gmail address letters go out from) and `SMTP_PASSWORD` (a Gmail **app password**, never the real password) in `.env`. Without them, letters can be written and approved but not sent.
3. Print or share `docs/pilot/CONSENT.md`. **No signed consent, no case.**
4. Choose volunteers whose company is in the verified directory (`backend/app/directory/companies.json`) and whose complaint is real and current.

## Giving each volunteer their own access code (new)
1. `python scripts/pilot_users.py add "Volunteer A"` prints a personal code **once**. Give it to that person privately (not in a group chat).
2. On the volunteer's phone the app asks for the code on first start and keeps it in the phone's secure storage ("Sign out of this phone" removes it).
3. Each person sees **only their own cases**. A wrong code gets "not right". `python scripts/pilot_users.py revoke u2` stops a code at once. `python scripts/pilot_users.py list` shows ids and labels, never codes.
4. Only the builder (the "owner": the shared token or this computer) can use "Call for me", because practice calls ring the builder's phone.
5. **Letters sent from the app go out from the builder's email account** (the pilot sender), signed with the volunteer's name. Tell each volunteer this before they tap Send. Company replies come to the builder's inbox. The volunteer's own cases only show replies that quote the case reference or answer the exact message (not sender-only matches).

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
