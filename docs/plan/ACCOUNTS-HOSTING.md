# Accounts and hosting plan (written 2026-11-21)

Goal: stay at zero cost, keep private data safe, and make the pilot work for people who are not the builder. Nothing here is built yet except what is marked "built".

## Why we need it
1. **Accounts:** today one shared token protects the whole backend, so every volunteer would see every case. Each person must only ever see their own cases.
2. **Hosting:** the backend runs on the builder's laptop and needs the same Wi-Fi. The voice server also needs a public https address that Twilio or FreJun can reach. On the builder's home network the Cloudflare tunnel is blocked, which is the most likely reason the 19 Nov line test failed. A small always-on server with its own public address removes the tunnel.
3. **Database:** cases live in one encrypted file (built). That is fine for a pilot of a few people and not for many users.

## Facts checked on 2026-11-21 (free tiers change often: re-check the page before relying on a number)
| Service | What we found | Doubt |
|---|---|---|
| Supabase free plan ([pricing](https://supabase.com/pricing)) | About 500 MB database, 50,000 monthly active users, 5 GB egress; a free project **pauses after about 7 days without activity**; no backups on the free plan | Sources disagree on details; whether the Mumbai region is available on the free plan was not confirmed |
| Oracle Cloud Always Free ([docs](https://docs.oracle.com/iaas/Content/FreeTier/resourceref.htm)) | The Arm VM allowance was **halved in 2026** (about 2 cores and 12 GB total now). A VM is treated as **idle and can be reclaimed if its 95th percentile CPU stays under 20% for 7 days**, which would fit a quiet app like ours | Card requirement and Mumbai or Hyderabad availability not confirmed; capacity varies by region |
| Azure for Students ([offer](https://azure.microsoft.com/en-us/free/students/)) | $100 credit for 12 months, **no credit card**, verified through the school email; one account per person; limited supply | Whether an SRM address qualifies, and prices in the Central India region, not confirmed |
| GitHub Student Developer Pack ([pack](https://education.github.com/pack)) | Offers change often; a third-party page says the DigitalOcean student credit ended after 31 Jul 2026 (unconfirmed on GitHub's page) | Check the live list before counting on any credit |

## Hosting options
| Option | Cost | Good | Bad |
|---|---|---|---|
| A. **Laptop for the pilot (now)** | 0 | Works today, nothing new to learn, data stays with the builder | Same Wi-Fi only; laptop must be on; no public address for phone calls |
| B. **Azure for Students VM** (recommended target) | 0 while the $100 lasts; stop the VM when idle to stretch it | No card; a normal always-available server with a public address and a region in India | Credit runs out in about a year or sooner; needs the SRM email to qualify; the builder must create the account |
| C. Oracle Always Free | 0 | Generous when it works | Idle-reclaim risk, halved allowance, signup often needs a card; do not depend on it |
| D. Free web hosts that sleep | 0 | Easy | Sleep after idle (a phone callback would time out), often need a card, little or no disk |

**Decision:** run the pilot on A. Build B as the real home once the builder confirms the student offer works. Keep the app and backend free of anything tied to one provider.

## Accounts, in three small steps
- **Step 0, BUILT (21 Nov, small, no outside service): a token per person.** Each volunteer gets their own secret token. The backend maps the token to a user id, stores the owner on every case and draft, and every read, write and delete is limited to that owner. A wrong owner gets "not found". Tests: person A cannot read, change, send from or delete person B's case, and cannot see B's drafts or call B's transcripts. This is enough for a 3-person pilot.
- **Step 1: real login with Supabase Auth.** Email and password, handled by Supabase (the free plan allows 50,000 users). The app signs in through Supabase's web interface and sends the user's login token; the backend checks its signature. Password reset comes from Supabase. **No phone-number OTP login:** it costs money for texts and it is the one thing Nivaran tells users never to share.
- **Step 2: a real database.** Move the encrypted file to Postgres with row-level rules so the database itself refuses cross-user reads. Do it when there are more users than one laptop can hold, and not before.

## The voice server in the cloud
Put the voice server on the same VM with a public https name (a free subdomain, with a free Let's Encrypt certificate via Caddy). Then Twilio or FreJun reach it directly, with no tunnel. The home network's Cloudflare problem stops mattering for calls. Real company calls stay off until the founder says go, and still need the provider's verification and the TRAI declaration (see `docs/notes/phone-teler-and-trai.md`).

## Privacy and safety to keep when hosted
- Region in India where possible (DPDP: some data may have to stay in India).
- Encrypted case files and backups; the key is not in the repository.
- The AI services (Groq, Gemini free tier) can read what users type: the paid or self-hosted route is a **precondition for real users**, not for the 3-person pilot with written consent.
- Add the one-page breach plan and a privacy contact page before inviting anyone outside the pilot.
- Server logs must not hold case text. (Check this before going live.)

## Who does what
| Step | Builder (you) | Claude |
|---|---|---|
| 0. Token per person | Tell me the volunteers' first names or labels | Build and test it |
| Confirm the student cloud offer | Sign up at azure.microsoft.com/free/students with your SRM email and tell me if it worked | Read the region and price pages |
| Create the VM | Click through the portal or accept the invite I give you | Write the setup script (Python, Caddy, systemd), the `.env` template and the deploy steps |
| 1. Supabase Auth | Create the free Supabase project (ask me for the settings) | Backend token check, app login screen, tests |
| Domain name | Choose a free subdomain | Caddy config |
| Go live checklist | Review and approve | Write it, run the tests, check the logs hold no case text |

## Order and timing
Exams are 25 Nov, 30 Nov, 1 Dec and 4 Dec; 24 Nov, 29 Nov and 3 Dec are rest days.
1. Before 7 Dec: Step 0 (per-person tokens) and the pilot on the laptop.
2. After 4 Dec: confirm the student offer, build the VM setup script, move the pilot server there if it works.
3. January: Supabase Auth and real accounts, then Postgres only if needed.

## Status of Step 0 (built 2026-11-21)
- `backend/app/users.py`, `app/auth.py`, `scripts/pilot_users.py`; tests in `backend/tests/test_isolation.py` (11): one person cannot read, change, approve, send from, delete, call about or even detect another person's case or draft (a foreign id answers exactly like a missing one); only the owner can place calls; sender-only reply matches are for the owner; tokens are stored hashed (the file never holds a token); revoking works at once; speech-to-text works for any signed-in person.
- App: an "enter your access code" screen, the code kept in the phone's secure storage, and a Sign out button.
- **Limits, honestly:** this is not a login system (no email, no password reset, no expiry; a lost code needs the builder). The builder can read every case on the laptop. Letters go out from one shared sender account. A full login comes with Step 1.
