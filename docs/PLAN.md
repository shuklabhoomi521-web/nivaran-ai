You are the lead engineer on a project called **Nivaran**. I am the founder. I am an ECE student who knows deep learning, is learning ML and app development, and will build this whole project with you. Read this entire message carefully before doing anything. It explains what we are building, how we work, and every stage from start to finish.

Explain things to me in simple words. Short sentences. When you use a hard term, explain it in one line.

---

# PART 1 — WHAT WE ARE BUILDING

## The one-line idea
Nivaran (Hindi for "solution") is one app that handles any company's customer care for the user. The user tells it the problem once, in their own language. The app contacts the company, talks for them, and does not give up until the problem is solved.

## The problem it solves
Every company has customer care: food delivery, shopping, telecom, banks, UPI apps, airlines, trains, cabs, appliances, electronics. Every one is painful: phone menus ("press 1 for…"), long hold times, repeating yourself, being ignored. Elders and non-tech users suffer the most. Nobody has built a good solution for India: Indian languages, Indian companies, Indian complaint escalation.

## What the user does
1. Opens the app. Types or speaks the problem. Example: "My Swiggy order came cold and they didn't refund me."
2. Picks a language (Tamil, Hindi, Telugu, English, Hinglish, and more).
3. Taps Go.

## What the app does
1. **Understands** the problem: company, category, what the user wants (refund, repair, replace, cancel, info).
2. **Asks only what is missing** (for example an order ID). Never invents details.
3. **Finds the official contact** from our own verified company directory.
4. **Picks the best channel:** phone call, email, or written complaint.
5. **Handles the call:** presses menu buttons, waits on hold, talks to the agent, explains, pushes politely.
6. **Handles verification safely** (OTPs and other proof — see the safety rules).
7. **Pulls the user in only when needed:** "The agent wants to talk to you. Tap to join."
8. **Escalates if ignored:** customer care → company grievance officer → National Consumer Helpline. Writes every letter.
9. **Reports back:** short summary, full transcript, next steps.

## Languages
The user speaks to the app in any language they choose. The AI speaks to the company in whatever language the company uses. Example: a grandmother explains in Tamil; the AI handles the call in English.

## Feature list
- Any category of company
- Any language (user side and company side handled separately)
- AI phone calls (menus, hold, live conversation)
- Complaint emails with follow-ups
- Escalation ladder
- Smart OTP handling (4 layers, below)
- Live join (user can listen or jump into the call anytime)
- Case tracker (every complaint, status, proof)
- Menu memory (remembers each company's phone menu path; next call is faster)
- Proof locker (bills, photos, screenshots saved with each case)

## OTP handling — 4 layers
1. **Auto-read:** with the user's permission, read the OTP from notifications. Only from that company's sender, only during a call the user started, processed on the phone.
2. **Avoid OTP:** first offer other proof (order ID, booking ID, registered email, last 4 digits).
3. **One-tap:** lock-screen notification "Share OTP with <company>? Yes / No".
4. **Pause and resume:** if no reply, ask the agent for a callback or retry later.

---

# PART 2 — HOW IT IS BUILT

## Architecture (four parts)
- **Mobile app** — the window. User raises problems, watches live calls, sees cases.
- **Backend brain** — does the real work. Three modules: Understand problem (message → case + plan), Pick contact (from verified directory), Safety guard (blocks forbidden data).
- **Channels** — Phone calls, Email, Escalation ladder.
- **Database** — cases, company directory, menu memory, users.
- **Our own ML models** (Phase 9) — classifier, menu memory, success predictor.

## Tech stack
- Backend: Python 3.11+, FastAPI, Pydantic
- Database + auth: Supabase (Postgres)
- AI brain: Anthropic Claude API
- Voice pipeline: Pipecat
- Indian-language speech-to-text and text-to-speech: an Indian speech provider (for example Sarvam); keep it swappable behind an interface
- Phone calls: Exotel or Plivo (Indian numbers); keep it swappable behind an interface
- Mobile app: React Native + Expo, TypeScript
- ML: PyTorch + Hugging Face (MuRIL / IndicBERT)
- Tests: pytest (backend), Jest (mobile)

Before using any library or API, check its current documentation, because versions and prices change. If something in this plan is outdated or a better option exists, tell me and explain why before switching.

## Folder structure
```
nivaran/
  CLAUDE.md
  README.md
  .env.example
  .gitignore
  docs/
    PLAN.md
    notes/phase-N.md      (5-line notes per phase)
  backend/
    app/
      main.py
      api/                (routes)
      brain/              (understand, plan, pick contact)
      safety/             (safety guard)
      channels/
        phone/
        email/
        escalation/
      directory/          (company directory)
      models/             (Pydantic models)
      db/
    tests/
  mobile/                 (Phase 6+)
  ml/                     (Phase 9)
  scripts/
```

---

# PART 3 — HOW WE WORK (follow every time)

1. **One phase at a time.** Only build the current phase. Never start the next phase until I say so.
2. **Plan first.** At the start of each phase, show me a short plan (steps, files, tools) and wait for my OK.
3. **Small steps.** After each step, run the tests and show me the result.
4. **Tests for everything.** Every feature gets automatic tests. A phase is not done if any test fails.
5. **Explain as you go.** One simple line for every new concept.
6. **Secrets.** All keys live in `.env`. Never write a key in code, never print it, never commit it.
7. **Git and GitHub — you handle all of it, fully on your own:**
   - My GitHub login is already set up on this machine. Use it directly. Do not ask me to log in or do anything on GitHub.
   - Initialise git, create `.gitignore`, make clean commits with clear messages after each working step.
   - Create the GitHub repo `nivaran` yourself (with the GitHub CLI `gh` or git, whichever is already authenticated). Make it private for now.
   - Push after every working step. At the end of each phase, create a tag `phase-N-done` and push it.
   - Write the README, keep it updated, and manage branches if useful. Never force-push over history and never delete the repo.
   - If an auth error ever happens, try the other authenticated method first; only tell me if both fail.
8. **End of every phase, do all of this:**
   - Check every "Done when" item. For each: done / partly / missing, with proof (test name, file, or command I can run).
   - List the 3 weakest parts of what we built and how to fix them.
   - Write `docs/notes/phase-N.md`: what we built, what broke, what we learned (5 lines).
   - Tell me what to record as a 30-second demo clip.
   - Update the "Current phase" line in CLAUDE.md.
   - Commit, tag, push. Then STOP and wait for me.
9. **Do everything yourself except these few things** (tell me exactly when and how, step by step, then wait):
   - Creating accounts on outside services and getting their API keys (Anthropic, Supabase, phone provider, speech provider). You set up everything around them; I only paste the keys into `.env`.
   - Anything that needs payment details or identity verification (KYC).
   - Phone permissions on my physical phone.
   - Saying OK before each real call to a real company (this is a safety rule, not a skill limit).
   Group these asks together so I'm interrupted as little as possible.
10. **Design for the future, build for now.** Keep the code ready for future scope, but do not build it early.

---

# PART 4 — SAFETY RULES (never break these, in any phase)

- Never share, store in plain text, or let the AI speak: UPI PIN, card number, CVV, passwords, or any OTP that approves a payment. Build this as a hard block in the safety guard, with tests that try to trick it.
- Only use company contacts from the verified directory. Every entry must have an official source link and a "checked on" date. Never use a number from web search results (fake helpline numbers are a common scam).
- Every outgoing call starts with the AI saying it is an AI assistant calling on behalf of the user. It never pretends to be the user.
- The user approves every email before it is sent.
- Private user details are stored encrypted.
- The user can stop any call or action at any time.
- When reading emails, SMS or other apps: read only. Never buy, pay, cancel or change anything. Show what was found and wait for a yes.

---

# PART 5 — THE ROADMAP (11 phases)

## Phase 0 — Setup (3–4 days)
Goal: every tool ready; nothing blocks us later.
Tasks:
- Create `CLAUDE.md` containing Part 1 summary, Part 2 stack, Part 3 rules, Part 4 safety rules, and a "Current phase" line. Create `docs/PLAN.md` containing this whole message.
- Create the folder structure above.
- Python virtual environment, `requirements.txt`, minimal FastAPI app with `/health` returning `{"status": "ok"}`.
- `.env.example` listing every key we will need in later phases (no real values). `.env` in `.gitignore`.
- One pytest test for `/health`.
- README with how to run.
- git init, create the private GitHub repo yourself using my existing login, first push.
- Give me ONE short checklist of accounts to create (Anthropic API, Supabase, phone provider, speech provider) with simple steps and where to paste each key. We only need the Anthropic key for Phase 1; the rest can wait until their phase.
Done when:
- [ ] `/health` runs locally and its test passes
- [ ] `.env` is ignored by git
- [ ] CLAUDE.md and docs/PLAN.md exist
- [ ] Repo on GitHub, tagged `phase-0-done`

## Phase 1 — The brain, text only (1 week)
Goal: the user types a problem in any language; the AI turns it into a clean case and a plan.
Tasks:
- `Case` model: company, category, problem_summary, user_goal (refund/repair/replace/cancel/info/other), details_known, details_missing, user_language, urgency.
- `POST /cases/understand`: sends the message to Claude, returns a filled Case using structured output.
- If details are missing, return ONE short follow-up question in the user's language. Never invent details.
- `POST /cases/plan`: best channel (call/email/complaint), opening line, proof the user should keep ready.
- Simple web chat page to test both endpoints.
- Test set of 30 problems: 8+ categories; English, Hindi, Tamil, Hinglish. Tests check each becomes a correct case.
Done when:
- [ ] All 30 test problems become correct cases
- [ ] Missing details are asked, never invented
- [ ] All tests pass; tagged `phase-1-done`

## Phase 2 — Company directory (1 week)
Goal: trusted official contacts for companies in every category.
Tasks:
- Supabase table `companies`: name, aliases, category, helpline numbers, emails, grievance officer name and email, working hours, channel notes, source_url, checked_on.
- Seed script and data file for 40 companies across 10 categories. You prepare the structure and a list of companies; I will verify each contact on the official website (or you fetch the official page and show me the source for each so I can confirm).
- The brain now matches the right company and picks the right contact and channel.
Done when:
- [ ] 40 companies, every entry has an official source_url and checked_on
- [ ] No contact taken from random search results
- [ ] Correct contact picked for all 30 test problems; tagged `phase-2-done`

## Phase 3 — Voice in the browser (1 week)
Goal: I talk to the AI out loud, in my language; it talks back. No phone yet.
Tasks:
- Pipecat pipeline: speech-to-text → Claude → text-to-speech, behind swappable interfaces.
- Interruptions: if I talk while the AI is speaking, it stops and listens.
- English, Hindi, Tamil, Hinglish.
- Measure reply delay; target about 1.5 seconds.
Done when:
- [ ] Full conversation works in all 4 languages
- [ ] Interruptions work
- [ ] Delay measured and written in notes; tagged `phase-3-done`

## Phase 4 — First real phone call, to a friend (1.5 weeks)
Goal: the AI calls a real phone; my friend pretends to be an agent.
Tasks:
- Connect the voice pipeline to the phone provider.
- AI disclosure line at the start of every call.
- A fake phone menu (IVR) we host ourselves, so the AI learns to press buttons (DTMF tones).
- Hold-music detection: wait quietly, don't hang up.
- Save full transcript of every call.
- "Join call" so I can jump in live.
Done when:
- [ ] 10 test calls, at least 8 handled well
- [ ] Gets through the fake menu every time
- [ ] Waits through 5 minutes of hold music
- [ ] Live join works; tagged `phase-4-done`

## Phase 5 — First real company calls (1.5–2 weeks)
Goal: solve real problems with real companies.
Tasks:
- 5 real small problems in different categories (I will provide them).
- Before EACH real call, show me the full plan and wait for my OK. I listen live every time.
- Fix every weak spot found.
- Save each company's menu path (menu memory, simple version).
Done when:
- [ ] At least 3 of 5 solved by the AI
- [ ] Every call ended safely
- [ ] One great call recorded for the demo (with permission); tagged `phase-5-done`
- Tell me: "You can start applying for internships now."

## Phase 6 — Mobile app (2 weeks)
Goal: a clean Android app anyone can use.
Tasks:
- React Native + Expo, TypeScript.
- Screens: login, new problem (type or speak), language choice, live call view, case list, case details with transcript.
- Push notifications ("Refund approved", "Agent wants to talk to you").
- Large text and simple layout, friendly for elders.
Done when:
- [ ] A friend who never saw it raises a problem without help
- [ ] Live call view updates in real time
- [ ] Works on 2 Android phones; tagged `phase-6-done`

## Phase 7 — OTP and safety (1.5 weeks)
Goal: the 4 OTP layers plus hard safety rules.
Tasks:
- Write the safety tests FIRST, then the code. Try hard to break our own rules.
- OTP layers 1–4 exactly as described in Part 1.
- Hard block on payment OTPs, UPI PIN, card number, CVV, passwords.
- Encrypt private details at rest.
- Check current Play Store policy for notification access before building Layer 1, and tell me what it allows.
Done when:
- [ ] All 4 layers tested on real calls
- [ ] 20 trick tests all refused
- [ ] Safety review done; tagged `phase-7-done`

## Phase 8 — Email and escalation ladder (1.5 weeks)
Goal: if ignored, the AI goes higher, step by step.
Tasks:
- Complaint emails with proof attached, sent from the user's own email with permission; user approves each one.
- Automatic follow-up after a set number of days.
- Ladder: customer care → grievance officer → National Consumer Helpline.
- Each case shows its current step and what happens next.
Done when:
- [ ] Full ladder runs end to end on one test case
- [ ] Every email approved by the user before sending; tagged `phase-8-done`

## Phase 9 — Our own ML layer (1.5 weeks)
Goal: real ML/DL we built ourselves, with numbers.
Tasks (explain each ML step like I am learning it):
- **Problem classifier:** fine-tune MuRIL or IndicBERT to classify category and user_goal from multilingual complaints. Build the dataset (real anonymised cases + carefully generated examples), train/validation/test split, compare against a simple baseline (for example TF-IDF + logistic regression). Show results in a table per language.
- **Menu memory:** a graph of each company's phone menu that improves after every call; measure time saved on repeat calls.
- **Success predictor:** small model predicting which channel works best for a company + problem type.
- Results table ready for a research paper and resume.
Done when:
- [ ] Classifier beats the baseline, numbers recorded
- [ ] Menu memory measurably speeds up repeat calls
- [ ] Results table in docs; tagged `phase-9-done`

## Phase 10 — Real users and launch kit (2 weeks)
Goal: real people use it; everything ready to show companies.
Tasks:
- Play Store closed testing build (guide me through the console steps only I can do).
- Support 20–50 real users; collect feedback; fix top 5 problems.
- Polished README with architecture diagram, demo GIFs, setup steps, results.
- Help me write: a 1–2 minute demo video script, a short technical write-up, and a resume line with real numbers.
Done when:
- [ ] 20+ users, 30+ real cases
- [ ] README, write-up, demo script done; tagged `v1.0`

---

# PART 6 — FUTURE SCOPE (design for it, do NOT build until I ask)

## "Find it for me" mode
For elders who can't find an order ID. The user says "the mixer I ordered last week from Amazon is broken"; the app finds the order itself.
- First approach: with permission, search order confirmation emails and SMS.
- Later approach: open the company's app and read "My Orders" using Android accessibility (fragile; check Play Store rules first).
- Show what was found and wait for a yes. Read only. Share only what the complaint needs.

## Family confirmation (son or daughter approves)
The elder links one or two trusted family members. When a confirmation is needed (OTP, sending an email, confirming the order) and the elder doesn't respond, taps "Ask my son/daughter", or the step is sensitive, the family member gets a notification: Approve / Reject / Call.
- Only the elder can add or remove family members.
- Family sees only what is needed for that one step.
- Payment OTPs, UPI PIN and card details are never shared, even with family approval.
- Every approval is logged: who, what, when.

Keep the data model ready for these (for example a `trusted_contacts` table and an `approvals` log), but do not build the features yet.

---

# START NOW

1. Confirm in a few lines that you understand the project, the way we work, and the safety rules.
2. Point out anything in this plan that looks outdated, risky or unclear, with your suggestion.
3. Then show me your plan for **Phase 0 only**, and wait for my OK before building.
