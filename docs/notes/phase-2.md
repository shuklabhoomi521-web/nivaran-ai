# Phase 2 notes: company directory

## Summary (5 lines)
- Built: 40-company directory (10 categories) in `backend/app/directory/companies.json`, built by `scripts/build_directory.py` from `scripts/directory_src.py`; every contact has its exact line from an official page.
- Built: lookup by name/alias/spelling, a contact picker (channels from what the directory really has), and `/cases/plan` now returns the official contact and fixes impossible channels (no call for Swiggy, Zomato, Zepto).
- Result: all 30 problems match the right company; 25 of 25 named-company problems get a verified contact (`docs/phase2-contact-check.md`). 269 free tests pass.
- Broke: many official sites block scripts or hide contacts behind JavaScript/login; search summaries and an AI "second check" were sometimes wrong or stale (BSNL's page no longer exists). Fixed by reading pages in a real browser and keeping exact quotes.
- Learned: top Indian apps (Swiggy, Zomato, Zepto) officially have no customer phone line, so "AI phones the company" is not possible for them. Only 10 of 63 phone numbers are confirmed on 2 official pages.

## Done-when check
| Item | Status | Proof |
|---|---|---|
| 40 companies, every entry has an official source link and checked date | **Done** | `test_forty_companies_across_ten_categories`, `test_every_source_is_official_https_and_dated` (host must be an official domain, https, dated, quote present). Indian Railways has only its main page, no contacts yet. |
| No contact taken from random search results | **Done** (founder verified) | Every contact has an exact quote and an official-domain source, checked by tests; founder checked the list by hand (Myntra and Ola personally). 81 of 124 sources were also re-found on the live page by script; the other 43 were read in a real browser. |
| The brain picks the right contact for all 30 test problems | **Done** | `docs/phase2-contact-check.md`: 30/30 right company; 25/25 named-company problems have a verified contact; the 5 problems with no company get a question and no contact. Uses saved AI answers (no new API calls). |
| Tagged `phase-2-done` | Done | tag pushed |

## 3 weakest parts
1. **Thin confirmation.** 53 of 63 phone numbers are `single_source`; 43 of 124 sources were read in a browser, not re-checked by script; 12 companies still have `needs_check` items; Indian Railways has no contact. Fix: add Play Store listings as second sources, re-read the browser-only pages on a schedule, fill the gaps.
2. **Goes stale.** Helplines change and nothing warns us. Fix: monthly `build_directory.py --refresh` job that flags any quote no longer found, and show `checked_on` age in the app.
3. **Picker is simple.** It takes the first suitable phone by label and role. It does not know which line fits the problem (BSNL landline vs mobile, Jio Fiber vs Mobile, Airtel prepaid vs DTH). The new `/cases/plan` was tested with a fake AI, not live. Fix: add `applies_to` to contacts, then run a small live plan test.

## Demo clip (30 seconds)
Open `http://127.0.0.1:8000/chat`. Type "Swiggy ne mera order cancel kar diya, paise wapas nahi mile", press Go, then Make plan. Show: the AI wanted a call, but the response says a call is not possible (Swiggy has no phone line) and switches to a complaint email with the official grievance address and the exact quote from Swiggy's page. Then try a made-up company and show "not in our verified directory. We never use a number from a web search."

## Open items
- Exotel KYC answer (founder emailed hello@exotel.com): see `docs/TODO-research.md`.
- Remaining `needs_check` items: see `docs/directory-verification.md` (search "NEEDS CHECK").
