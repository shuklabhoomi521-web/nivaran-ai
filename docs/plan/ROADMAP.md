# Nivaran roadmap (public version)

Rule for the whole plan: nothing costs money, nothing is guessed, every claim is tested. The detailed day-by-day calendar and personal schedule are kept outside the repository.

## Phone is a core channel, with fallbacks
Nivaran's promise is that it makes the call. Some problems (banks, telecom) need a call even after email and chat. Email, company chat and official portals are fallbacks when a call fails or ends unresolved.

| Channel | How it works | Cost |
|---|---|---|
| Phone call (core) | The app places the call for the user, says it is an AI, follows menus, escalates | Provider credit; going live needs provider verification and the TRAI A2P declaration (see `docs/notes/phone-teler-and-trai.md`) |
| Grievance email to the official grievance officer | The app writes the letter, the user approves and sends, the app tracks replies | Free |
| Company chat / WhatsApp | The app prepares the message, the user sends it | Free |
| Official portals (consumer helpline, RBI, IRDAI, AirSewa, TRAI, e-Daakhil) | The app picks the portal, writes the complaint, the user files it, the app stores the docket number | Free |

## Chapters
- **C0 Setup:** free accounts, clean repo, all tests green.
- **C1 Phone first:** rules, vendor replies, a real test call to the builder's own number, decision on how calls go live. Output: `docs/REAL-WORLD.md`.
- **C2 Directory v2:** 40 to 100 companies with grievance email, appellate authority, regulator, chat link, official source and quote.
- **C3 Case and email engine:** case states and timeline (day 0, 3, 7, 15), letter writer, send-with-approval, reply tracking.
- **C4 Regulator kits:** complaint generators and checklists per portal, verified against the live pages.
- **C5 Mobile app (Expo):** new case, case list, case detail, approve and send, reminders.
- **C6 Voice:** voice intake and spoken summary in Hindi, Tamil, English.
- **C7 Hosting, privacy, safety:** free hosting, login, encryption, red-team tests, DPDP basics (`docs/notes/dpdp-basics.md`).
- **C8 Phone in the app:** "Call for me" screen with consent and AI disclosure, and automatic fallback from a failed call to email and portal.
- **C9 Pilot:** a few volunteers with real complaints (written consent), results table.
- **C10 Polish:** installable Android app, docs, new demo video.

## Daily routine
1. Do the day's one task. Claude keeps `PROGRESS.md` (done, next, blocked).
2. Every day ends with tests green, commit, push.
3. Every 7th work day is a buffer. If a task slips, it moves to the next buffer.

## Risks and fallbacks decided now
| If this fails | We already have |
|---|---|
| Free AI limits (Groq, Gemini) | Automatic backup between the two, local Whisper, Sarvam credit |
| Company has no grievance email | Directory keeps chat/WhatsApp and the sector regulator portal |
| Phone rules unclear or provider needs verification | Phone stays optional; the app is complete without it |
| No free hosting | Laptop plus a free tunnel for the pilot |
| Wrong facts in a complaint | Letters use only facts the user gave; the user approves every email; tests |
| Privacy | Encrypted private fields, delete-my-data button, consent screen, no OTP or card ever |
