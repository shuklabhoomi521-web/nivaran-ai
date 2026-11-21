# Directory v2 (started 2026-11-20)

## What changed
- New optional fields per company: `appellate_authority`, `chat_channels` (in-app, web chat, WhatsApp).
- New verified regulator table by category: `backend/app/directory/regulators.json` (official page and exact quote each). AirSewa and e-Daakhil are marked needs-check, not invented.
- 9 companies added on 2026-11-20 (49 total): ICICI Bank, Punjab National Bank, Bank of Baroda, Tata Power-DDL, BESCOM, Canara Bank, ACT Fibernet, Indraprastha Gas, HP Gas. Quotes were read by a page-reading tool and are marked `machine_checked: false`; our re-check script has not run on them yet. Several entries carry `needs_check` notes (for example PNB's support email is printed obfuscated on the official page, so it is not stored as a checked contact).

## Added on 2026-11-22 (58 total)
Axis Bank, Kotak Mahindra Bank, Bajaj Allianz General Insurance (now Bajaj General Insurance), Niva Bupa, IDBI Bank, Air India Express, BigBasket, Blinkit, Ajio. Read in a real browser; all `machine_checked: false`. Notes:
- Blinkit has no phone (site says so, stored as `official_no_phone`); only info@blinkit.com is stored.
- Ajio: only the grievance officer email (from the Terms page); no phone printed.
- BigBasket's contact page looks like an old layout; confirm the number before relying on it.
- Removed the alias "Air India Express" from Air India (it is its own entry now).

## Planned but NOT added (checked 2026-11-22)
| Company | Why not | What to do |
|---|---|---|
| MakeMyTrip | makemytrip.com/support pages return 503; the new support and escalation pages (supportz.makemytrip.com) need a login and show no contact lines | Retry later, or read from a logged-in session by hand |
| Whirlpool India | whirlpoolindia.com redirect is paused (RedirHub); india.whirlpool.in /support and /contact-us are 404, home page text has no contact lines | Find the Support menu page by hand |
| Union Bank of India | Browser refused the site (navigation denied/failed) | Retry later or read by hand |
| Bank of India | Cloudflare bot check ("Just a moment"); not bypassed | Read by hand in a normal browser |
| OYO | /contact-us is 404; support page is a chat assistant showing only a new-booking number (0124-4208080), not a complaint line; terms page text was empty | Find the grievance officer on the terms page by hand |
| Kotak and Axis (extra) | Stored phones only; Kotak grievance page and Axis Grievance Redressal tab not opened | Read officer/escalation pages for both |
| SBI Life | Not retried in this batch | Read in a browser |

Rule kept: no contact enters the directory unless its exact line from an official page is stored with it and the contact appears inside that line (enforced by tests).

## Second batch, also not added (site refused or returned nothing on 2026-11-20)
Union Bank of India (connection refused), Bank of India (403), IDBI Bank (moved to idbi.bank.in, not read), New India Assurance (page empty or timed out), ICICI Prudential Life (403), Indane/Indian Oil (redirect and script-only page), Bharat Gas/BPCL (403), Mahanagar Gas (403), Air India Express (script-only page), OYO (contact pages 404), Tata Power Mumbai (no contact lines in the page text). Read these in a browser and copy the exact lines, or retry later.
