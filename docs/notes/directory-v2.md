# Directory v2 (started 2026-11-20)

## What changed
- New optional fields per company: `appellate_authority`, `chat_channels` (in-app, web chat, WhatsApp).
- New verified regulator table by category: `backend/app/directory/regulators.json` (official page and exact quote each). AirSewa and e-Daakhil are marked needs-check, not invented.
- 9 companies added on 2026-11-20 (49 total): ICICI Bank, Punjab National Bank, Bank of Baroda, Tata Power-DDL, BESCOM, Canara Bank, ACT Fibernet, Indraprastha Gas, HP Gas. Quotes were read by a page-reading tool and are marked `machine_checked: false`; our re-check script has not run on them yet. Several entries carry `needs_check` notes (for example PNB's support email is printed obfuscated on the official page, so it is not stored as a checked contact).

## Planned but NOT added (could not be read from the official site on 2026-11-20)
| Company | Why not | What to do |
|---|---|---|
| Axis Bank | Pages moved to axis.bank.in; contact numbers only came from a summary, not word for word | Read the contact page in a browser, copy the lines |
| Kotak Mahindra Bank | Emails printed obfuscated; numbers only from a summary | Same |
| Ajio, Blinkit, SBI Life | Site refuses automated readers (HTTP 403) | Read in a browser |
| BigBasket | contact page 404, FAQ had no contacts | Find the current help page by hand |
| Bajaj Allianz | Old pages redirect to bajajgeneralinsurance.com and return 404 | Find the current contact page |
| Niva Bupa | Page did not render | Read in a browser |
| Whirlpool India | Old site shows a paused redirect | Use india.whirlpool.in support page by hand |
| MakeMyTrip | Pages timed out | Retry later |

Rule kept: no contact enters the directory unless its exact line from an official page is stored with it and the contact appears inside that line (enforced by tests).

## Second batch, also not added (site refused or returned nothing on 2026-11-20)
Union Bank of India (connection refused), Bank of India (403), IDBI Bank (moved to idbi.bank.in, not read), New India Assurance (page empty or timed out), ICICI Prudential Life (403), Indane/Indian Oil (redirect and script-only page), Bharat Gas/BPCL (403), Mahanagar Gas (403), Air India Express (script-only page), OYO (contact pages 404), Tata Power Mumbai (no contact lines in the page text). Read these in a browser and copy the exact lines, or retry later.
