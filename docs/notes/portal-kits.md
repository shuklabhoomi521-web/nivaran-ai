# Regulator portal kits (sprint day 5-6 work, built 2026-11-21)

Code: `backend/app/cases/kit.py`, `backend/app/directory/regulators.json`, `GET /tracked-cases/{id}/portal-kit`. Tests: `backend/tests/test_portal_kit.py`.

## What a kit gives the user
The regulator for the case's category (National Consumer Helpline, RBI CMS, IRDAI Bima Bharosa, TRAI, Rail Madad), its official link and helpline, the steps, what to attach, a checklist, warnings, and a complaint text to paste. **The user files it by hand.** The app never types a password, OTP, PIN or card detail on a portal.

## How honesty is enforced
- Every step or attachment line is either **official** (it stores an exact quote and the official page URL) or **ours** (labelled as our own checklist). A line with neither cannot be created (a test checks this).
- Anything we could not verify is listed under `needs_check`, never presented as a rule.

## What was verified on 2026-11-20 and what was not
| Regulator | Verified from the official page | Not verified (needs check) |
|---|---|---|
| National Consumer Helpline | Registration, docket number, tracking, up to 30 days, Consumer Commission as next step, helpline 1915 and 1800-11-4000 | Document list, fees |
| IRDAI Bima Bharosa | Complain to the insurer first; then IRDAI; only the insured or claimant can complain; form must be complete; no payment asked | Number of days to wait (the page says only "a reasonable period of time") |
| RBI CMS | Portal purpose; contact centre #14448 | Bank-first rule, waiting period, documents, fee: the scheme text was behind a bot check |
| TRAI (telecom) | Complain to the provider's complaint centre; then the appellate authority | Waiting time, documents |
| Rail Madad | Portal name and complaint sections | Filing steps and documents |
| AirSewa | nothing readable | everything; airline cases use the National Consumer Helpline and show this note |
| e-Jagriti | Named as a current portal on the NCH site (e-Daakhil's address no longer resolves) | Purpose, steps, fees |

## Not yet
Reading the RBI scheme text, AirSewa and e-Jagriti by hand and adding their quotes; the kit screen in the mobile app.
