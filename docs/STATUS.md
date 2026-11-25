# Nivaran project tracker

Updated 2026-11-26 02:10. v1.0 target: Mon 7 Dec 2026. Backend and app are built and tested; the open items are the demo video, the pilot, and anything that needs a phone provider.

**18 of 37 items done (49%).** In progress: 2 · Planned next: 8 · Needs you: 6 · Waiting: 1 · Blocked: 2


## Backend (Python, FastAPI)

| Status | Item | Detail |
|---|---|---|
| Done | Case tracker with the day 0 / 3 / 7 / 15 escalation ladder | Engine plus API, owner-only access |
| Done | Verified company directory: 58 companies | Every contact has its official page and exact quote. 5 sites refused to be read (Union Bank, Bank of India, MakeMyTrip, Whirlpool, OYO) |
| Done | Letters from the user's own facts, approve before send | Template only, no AI text, sent only to directory addresses |
| Done | Reply tracking (read-only inbox) | Strong and weak matches; weak ones go to the owner only |
| Done | Portal kits: helpline, RBI, IRDAI, TRAI, Rail Madad, AirSewa, e-Jagriti | AirSewa and e-Jagriti filled from the official pages on 26 Nov (case type, documents list, fee table). Gaps are listed, not hidden |
| Done | Privacy and safety | Encrypted storage, consent notice, 18+ check, retention, personal access codes, encrypted user profile |
| Done | One link: the backend serves the web app at /app | http://localhost:8000/app/ while the backend runs |
| Done | 643 automated backend tests pass | Plus 4 known gaps recorded as expected failures |
| Planned next | Court-ready summary from the case timeline | e-Jagriti asks for a 'Synopsis with List of Dates and Events'; our timeline already holds those dates |
| Planned next | Per-company response times | Today follow-up dates use the standard 3 / 7 / 15 day ladder, not each company's own stated time |
| Planned next | Read RBI scheme text and Rail Madad steps by hand | Both kits are partial |

## App and front end (React Native + web)

| Status | Item | Detail |
|---|---|---|
| Done | Professional redesign (26 Nov) | Navy navigation, flat white panels, summary figures, status badges; glass and blur removed |
| Done | Sign-in, one-time details form, dashboard, ongoing and resolved complaints, profile with numbers | Laptop (side bar) and phone (top bar) layouts |
| Done | Case screen: ladder, verified contact with source, letter, filing kit, reminders | 49 app tests pass |
| Done | Hindi and Tamil text (first draft) | Menus, dashboard, complaint cards. Not checked by a native speaker |
| Needs you | Try the app on a real phone | bash scripts/run_pilot.sh, then Expo Go. Only browser checks so far |
| Needs you | Get a native speaker to check the Hindi and Tamil text |  |
| Planned next | Android app file (APK) | Needs your free Expo account (npx eas-cli login) |

## Phone calls and voice

| Status | Item | Detail |
|---|---|---|
| Done | Voice agent, practice mode, safety rules in code | 9 of 10 practice calls passed; speech test 0.05 word error vs 0.42-0.51 |
| Needs you | Call FreJun support (+91 8035 301 939) for dashboard access and a sandbox key | You said you would call. Tell me what they say |
| Blocked | Real phone call proof | No provider works yet; Twilio could not reach our server through the tunnel |
| Done | Real calls to companies stay OFF by design | Needs a verified provider and TRAI declaration first |

## Hosting and accounts

| Status | Item | Detail |
|---|---|---|
| Done | Pilot runs on your laptop | scripts/run_pilot.sh |
| Blocked | Cloud server on Azure for Students | No cheap VM size allowed in South India; other regions not tested. Revisit later |
| Planned next | Real accounts (Supabase Auth) instead of access codes | After the pilot |

## Internship outreach

| Status | Item | Detail |
|---|---|---|
| Done | 76 companies emailed, plus 24 follow-ups | Only publicly posted hiring addresses. 8 follow-ups went out on 26 Nov |
| In progress | More follow-ups, 8 a day | All 8 follow-ups of 26 Nov are sent (24 follow-ups in total). About 12 companies are still due their first follow-up |
| Waiting | Replies: none positive yet | SuperKalam says it will revert in 1-3 days if shortlisted; CallMissed said no politely |
| Needs you | Send the LinkedIn messages (10 people) | Pack and 7 tailored resume PDFs are in LinkedIn_Outreach_Pack.zip on your Desktop |
| Needs you | Apply to SuperKalam's React Native internship | Needs your own Y Combinator login; use the SuperKalam resume |
| In progress | Find more startups with a public hiring address | Only 5 verified so far; most use forms |
| Planned next | Upload the demo video (GitHub release or LinkedIn) and link it in the README | Your call: public upload is your decision |

## Demo, docs and release

| Status | Item | Detail |
|---|---|---|
| Done | Demo video of the redesigned app (77 seconds, phone format, voice-over) | Fake user Asha Rao; shows dashboard, ladder with official source, approve-before-send letter, regulator filing kit, profile, Hindi. File: Desktop/Nivaran Demos/Nivaran_v1_app_demo_26Nov.mp4. Not yet uploaded anywhere |
| Done | LinkedIn pack and tailored resumes saved | docs in ~/nivaran-outreach (private) |
| Planned next | README and docs match the final app |  |
| Needs you | Pilot with 3 volunteers who sign the consent form | Kit is ready in docs/pilot/. Zero real pilot cases so far |
| Planned next | Tag v1.0 and push | After the video and at least a first pilot case |
