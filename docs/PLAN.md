<!-- Master prompt v2 (12 Oct 2026), converted from PDF text. Previous version is in git history. -->


Nivaran — AI Customer Care Agent: Project
Plan
​Oct 12, 2026

· ​@Bhoomi

What the app does
Nivaran (working name, Hindi for "solution") is one app that handles any company's
customer care for you. You tell it your problem once, in your own language. It contacts the
company, talks for you, and keeps going until the problem is solved.
The one-line pitch: Tell it once. It doesn't give up until it's fixed.

What the user does
1. Opens the app and types or speaks the problem. Example: "My Swiggy order came
cold and they didn't refund me."
2. Picks a language (Tamil, Hindi, Telugu, English, Hinglish and more).
3. Taps Go. That's it.

What the app does behind the scenes
1. Understands the problem. It finds the company, the category (food, telecom, airline,
bank, appliance…) and what you want (refund, repair, replacement, cancellation).
2. Asks only what's missing. For example, the order ID. Nothing else.
3. Finds the official contact. From its own verified list of helplines, emails and grievance
officers.
4. Picks the best channel. Phone call, email, or written complaint.
5. Handles the call. Presses the menu buttons, waits on hold, talks to the agent, explains,
and pushes politely.
6. Handles verification safely. OTPs, booking IDs, registered email (see the safety rules).
7. Pulls you in only when needed. "The agent wants to talk to you. Tap to join."
8. Escalates if ignored. Customer care, then grievance officer, then the National
Consumer Helpline. It writes every letter for you.
9. Reports back. A short summary, the full transcript, and what happens next.

Nivaran — AI Customer Care Agent: Project Plan

Full feature list
Feature

What it means in simple words

Any category

Food, shopping, telecom, banks, UPI apps, airlines,
trains, cabs, appliances, electronics

Any language

You speak your language; the AI speaks the
company's language

AI phone calls

It calls, presses buttons, waits on hold and talks for
you

Emails and complaints

It writes strong, polite complaints and follows up

Escalation ladder

If ignored, it goes higher, step by step

Smart OTP handling

Auto-reads safe OTPs, avoids OTPs when it can,
never shares payment OTPs

Live join

You can listen to the call live or jump in anytime

Case tracker

Every complaint, its status and its proof in one
place

Menu memory

It remembers each company's phone menu, so the
next call is faster

Proof locker

Bills, photos and order screenshots saved with
each case

How it works inside
The app has four parts: the mobile app you see, the brain on a server, three ways to reach
companies, and a database that remembers everything.

Nivaran — AI Customer Care Agent: Project Plan

Nivaran system · app, brain, three channels

Read it top to bottom: the user talks to the app, the brain understands and checks safety,
then it reaches the company by call, email, or escalation.

The tech we use
Part

Tool

Why this one

Backend (server)

Python + FastAPI

You already know Python; FastAPI is
simple and fast

Database + login

Supabase

Free to start; database and user
login in one place

AI brain (now)

Google Gemini API, free tier

Free, no credit card; good with
Indian languages

AI brain (later)

Your own fine-tuned opensource model

No outside API; built in Phase 9

Voice pipeline

Pipecat

Free tool made for voice AI; joins
speech, AI and phone

Indian-language
speech

An Indian speech provider (e.g.
Sarvam)

Built for Indian languages and
accents

Nivaran — AI Customer Care Agent: Project Plan

Part

Tool

Why this one

Phone calls

Twilio trial (Phase 4), Exotel
with KYC (Phase 5)

Trial for testing; Exotel for real
company calls

Mobile app

React Native + Expo

One code for Android and iPhone

Your own ML

PyTorch + Hugging Face

Fine-tune open-source models for
free on Colab/Kaggle

Prices and features change, so check each tool's current free plan in Phase 0.

Where to start: backend first
We start with the backend (the brain on a server), not the app screens.
Why:
The magic of this app is the AI that understands, calls and argues. That lives in the
backend.
The mobile app is only a window into the brain. A window is easy to build once the brain
works.
If the screens come first, you get a pretty app that can't do anything. That impresses
nobody.
So the order is: brain → phone calls → app screens → safety → escalation → your own ML
→ real users.
Until the mobile app is ready, we test everything with a simple web page and the terminal
(the black command window).

The rules for moving step by step
We move to the next phase only when every box in the current phase's "Done when" list is
ticked. No exceptions.
1. One phase at a time. Never start Phase 4 work while Phase 3 has open boxes.
2. Test before you trust. Every phase has automatic tests. Tests = small programs that
check your code works. If a test fails, the phase is not done.
3. Save a checkpoint. At the end of each phase, save the code to GitHub with a tag like
phase-3-done . If something breaks later, you can go back.

4. Write 5 lines of notes. What you built, what broke, what you learned. You'll need this
for interviews and your research paper.

Nivaran — AI Customer Care Agent: Project Plan

5. Record a 30-second clip. A screen recording of the phase working. These become your
demo video later.
6. Ask Claude Code to review. Before closing a phase, ask it: "Review this phase against
the Done-when list. What is missing or weak?"
Small steps are fine. Skipped steps are not.

Roadmap: 11 phases, about 16 weeks
Each phase has a goal, the tasks, and a "Done when" checklist. Times assume you work
alone with Claude Code, a few hours a day.

Phase 0 — Setup (3–4 days)
Goal: Every tool and account ready, so nothing blocks you later.
Tasks:
Install Python, Node.js, Git, VS Code and Claude Code.
Create a GitHub repo called nivaran .
Create accounts: Anthropic API (the AI brain), Supabase (database + login), a phonecall provider (Exotel or Plivo, which give Indian numbers), and an Indian-language
speech provider (for example Sarvam).
Put all secret keys in a .env file. Never in the code.
Add the CLAUDE.md file from the Claude Code section below.
Done when:
Claude Code runs inside the repo and has read CLAUDE.md
A "hello world" backend runs on your laptop
.env is listed in .gitignore (so keys never reach GitHub)

First commit pushed, tagged phase-0-done

Phase 1 — The brain, text only (1 week)
Goal: You type a problem in any language. The AI turns it into a clean "case" and a plan.
Tasks:
Build a backend (FastAPI, a Python tool for making web servers).
Make a "case" format: company, category, problem, what the user wants, details
needed, language.
The AI reads the user's message and fills the case. If details are missing, it asks one
short question.

Nivaran — AI Customer Care Agent: Project Plan

The AI writes a plan: which channel to use and what to say.
Make a simple chat web page to test it.
Done when:
30 test problems across 8 categories and 4 languages all become correct cases
Missing details are always asked for, never invented
Automatic tests pass
30-second clip recorded, tagged phase-1-done

Phase 2 — Company directory (1 week)
Goal: A trusted list of official contacts for companies in every category.
Tasks:
Database table for companies: name, category, helpline numbers, emails, grievance
officer, working hours, notes.
Every entry stores where you got it (the official website link) and when you checked
it.
Fill 40 companies across 10 categories by hand from official websites.
The brain from Phase 1 now picks the right company and contact.
Done when:
40 companies, every entry has an official source link
Zero numbers taken from random Google results (fake helpline numbers are a common
scam)
The brain picks the right contact for all 30 test problems
Tagged phase-2-done

Phase 3 — Voice in the browser (1 week)
Goal: You talk to the AI out loud, in your language, and it talks back. No phone yet.
Tasks:
Add speech-to-text (turns your voice into words) and text-to-speech (turns words into
voice).
Use Pipecat, a free tool for building voice AI, to connect the pieces.
Make it fast: the AI should reply within about 1.5 seconds.
Support at least English, Hindi, Tamil and Hinglish.
Done when:

Nivaran — AI Customer Care Agent: Project Plan

A full conversation works in all 4 languages
You can interrupt the AI mid-sentence and it stops and listens
Reply delay measured and written in your notes
Tagged phase-3-done

Phase 4 — First real phone call, to a friend (1.5 weeks)
Goal: The AI calls a real phone. Your friend pretends to be a customer care agent.
Tasks:
Connect the voice AI to the phone-call provider.
At the start of every call, the AI says it is an AI assistant calling for the user.
Build a fake phone menu ("press 1 for…") so the AI learns to press buttons.
Detect hold music and wait quietly.
Save the full transcript of every call.
A "join call" button so you can jump into the call live.
Done when:
10 test calls with your friend, at least 8 handled well
The AI gets through the fake menu every time
It waits through 5 minutes of hold music without hanging up
You can join a live call successfully
Tagged phase-4-done

Phase 5 — First real company calls (1.5–2 weeks)
Goal: The AI solves real problems with real companies.
Tasks:
Pick 5 real small problems (yours, friends', family's) in different categories.
Let the AI call. You listen live every time, ready to jump in.
Fix every weak spot you hear.
Save each company's phone menu path for next time.
Done when:
At least 3 of 5 real problems solved by the AI
Every call ended safely (no wrong info shared)
One great call recorded for your demo video (with permission)
Tagged phase-5-done — you can start applying for internships now

Nivaran — AI Customer Care Agent: Project Plan

Phase 6 — The mobile app (2 weeks)
Goal: A clean Android app that anyone can use.
Tasks:
Build with React Native (one codebase for Android and iPhone) using Expo.
Screens: login, new problem (type or speak), language choice, live call view, case list,
case details with transcript.
Push notifications: "Your refund was approved", "Agent wants to talk to you".
Done when:
A friend who has never seen it can raise a problem without your help
Live call view shows what is happening in real time
Works on 2 different Android phones
Tagged phase-6-done

Phase 7 — OTP and safety (1.5 weeks)
Goal: The four OTP layers, plus hard safety rules.
Tasks:
Layer 1: with permission, read OTPs from notifications, only from that company, only
during a call the user started.
Layer 2: try other proof first (order ID, booking ID, registered email).
Layer 3: one-tap "Share OTP?" on the lock screen.
Layer 4: if no reply, ask for a callback or retry later.
Hard block: never share payment OTPs, UPI PIN, card number, CVV or passwords. Ever.
Keep private details encrypted (locked so only your app can read them).
Done when:
All 4 layers tested on real calls
20 "trick" tests (an agent asking for UPI PIN, card number, etc.) all refused
A friend reviews the safety rules and finds no gap
Tagged phase-7-done

Phase 8 — Email and the escalation ladder (1.5 weeks)
Goal: If the company ignores you, the AI goes higher, step by step.
Tasks:

Nivaran — AI Customer Care Agent: Project Plan

AI writes complaint emails with proof attached, sent from the user's own email (with
permission).
Automatic follow-up if no reply in a set number of days.
Ladder: customer care → grievance officer → National Consumer Helpline.
Each case shows which step it is on and what happens next.
Done when:
A complete ladder runs end to end on one test case
Every email is shown to the user before sending (the user approves)
Tagged phase-8-done

Phase 9 — Your own models: replace the outside brain (2–3 weeks)
Goal: Nivaran runs on models you trained and host, not on Gemini or anyone else's API.
This is what makes the project truly yours, and what impresses interviewers most.
Why it's possible: you don't build a brain from zero (that needs crores of rupees and huge
teams). You take a free open-source model (a ready-made smart brain anyone can
download, like Llama, Qwen or Gemma) and fine-tune it (teach it Nivaran's specific jobs).
Tasks, step by step:
1. Problem classifier (small model). Fine-tune MuRIL or IndicBERT to sort complaints by
category and goal. Compare it against a simple baseline and against the Phase 1 Gemini
scores.
2. Safety model. A small model, plus hard rules, that spots card numbers, PINs and OTPs
in any language. Must catch 100% of the trick tests.
3. Menu memory. A map of each company's phone menu that improves after every call.
Measure time saved on repeat calls.
4. Channel picker. A small model that guesses which channel works best for a company
and problem.
5. Own conversation brain (the big one). Fine-tune a small open-source chat model on
Nivaran's real call transcripts and letters. Test it on the same jobs Gemini does: talking
on calls, writing emails, summarising.
6. Swap step by step. Replace Gemini one job at a time with your own model, only when
yours scores close enough. Keep Gemini as a backup until then.
Where the computing power comes from:
Training: free GPUs on Google Colab and Kaggle (GPU = a powerful chip for AI training).

Nivaran — AI Customer Care Agent: Project Plan

Running all day: needs a server that's always on. Options: startup credit programs
(Google, Microsoft, AWS), the IndiaAI Mission's GPU access for startups and
researchers (check current rules), or a small paid server once the app has users.
Done when:
Your classifier beats the baseline, with numbers in a table per language
Safety model catches every trick test
Menu memory measurably speeds up repeat calls
Your own chat model handles at least the simple jobs (understanding and
summarising) as well as Gemini did in Phase 1
A results table: "our model vs Gemini" for every job, ready for your paper and resume
Tagged phase-9-done

Phase 10 — Real users and launch kit (2 weeks)
Goal: Real people use it, and you have everything to show companies.
Tasks:
Put the app on the Play Store (closed testing is fine).
Get 20–50 friends, classmates and family to use it.
Collect feedback and fix the top 5 problems.
Make: a 1–2 minute demo video, a clean GitHub README, a short write-up, and a
resume line with numbers.
Done when:
At least 20 real users, at least 30 real cases handled
Demo video, README and write-up done
Sent to at least 15 companies
Tagged v1.0

Claude Code: setup file and prompts
Claude Code reads a file called CLAUDE.md in your project folder every time it starts.
Think of it as the project's rulebook. Put it there in Phase 0. Then, for each phase, paste
that phase's prompt.

How to use the prompts
1. Open the terminal in your project folder and type claude .
2. Paste the phase prompt.

Nivaran — AI Customer Care Agent: Project Plan

3. Claude Code will first show a plan. Read it. Ask questions. Only then say "go ahead".
4. When it says the phase is done, paste the review prompt (at the end of this section).
5. Tick the Done-when boxes in this doc yourself. Don't just trust it.

CLAUDE.md (copy this whole block into the file)
# Nivaran — AI customer care agent
## What this project is
One app that handles any company's customer care for the user. The user
describes
a problem once, in any Indian language. The AI finds the official contact,
calls or
emails the company, handles the conversation, and escalates if ignored.
## Who I am
I am an ECE student learning ML and app development. Explain your choices in
simple words. When you use a hard term, explain it in one line.
## Tech stack
- Backend: Python 3.11+, FastAPI, Pydantic
- Database + login: Supabase (Postgres)
- AI brain: Anthropic Claude API
- Voice: Pipecat; Indian-language speech-to-text and text-to-speech
- Phone calls: Exotel or Plivo (Indian numbers)
- Mobile app (Phase 6+): React Native with Expo, TypeScript
- ML (Phase 9): PyTorch + Hugging Face (MuRIL / IndicBERT)
## How we work
- We build in phases. Only work on the current phase. Never start the next
one.
- Before writing code, show me a short plan and wait for my OK.
- Small steps. After each step, run the tests and tell me the result.
- Every feature gets automatic tests (pytest for Python).
- Keep code simple and readable. Comments for anything non-obvious.
- All secrets live in .env. Never write a key in code. Never print keys.
## Safety rules (never break these)
- Never share or ask the AI to speak: UPI PIN, card number, CVV, passwords,
or any OTP that approves a payment.
- Only use company contacts from the verified directory. Never a number
found by web search.
- Every outgoing call starts by saying it is an AI assistant calling for the
user.
- The user must approve every email before it is sent.

Nivaran — AI Customer Care Agent: Project Plan

- Private user details are stored encrypted.
## Current phase
Phase 0 (update this line at the start of each phase)

Phase 0 prompt
We are starting Phase 0 (Setup) of Nivaran. Read CLAUDE.md first.
Goal: a clean project skeleton so nothing blocks us later.
Please:
1. Create this folder structure: backend/ (FastAPI app), mobile/ (empty for
now),
ml/ (empty for now), docs/, tests/.
2. Set up a Python virtual environment and a requirements.txt.
3. Create a minimal FastAPI app with a /health route that returns {"status":
"ok"}.
4. Create .env.example listing every key we will need later (no real values),
and make sure .env is in .gitignore.
5. Add one pytest test for /health.
6. Write a short README with how to run it.
Show me the plan first. After building, run the test and show me the result.

Phase 1 prompt
We are starting Phase 1 (The brain, text only). Read CLAUDE.md first.
Goal: the user types a problem in any language, and the AI turns it into a
clean "case" plus a plan.
Please:
1. Define a Case model with: company, category, problem_summary, user_goal
(refund / repair / replace / cancel / info / other), details_known,
details_missing, user_language, urgency.
2. Build a POST /cases/understand endpoint. It sends the user's message to
Claude and returns a filled Case. Use structured output so the result
always matches the model.
3. If details are missing, return ONE short follow-up question in the
user's language. Never invent details like order IDs.
4. Build a POST /cases/plan endpoint that returns: best channel (call / email
/ complaint), what to say first, and what proof the user should keep
ready.
5. Make a very simple chat web page to test both endpoints.

Nivaran — AI Customer Care Agent: Project Plan

6. Create a test set of 30 problems: 8+ categories, in English, Hindi,
Tamil and Hinglish. Write tests that check each becomes a correct case.
Show me the plan first. Explain any hard term in one line.

Prompts for Phases 2–10
Same pattern each time: start with "We are starting Phase X. Read CLAUDE.md first.",
then paste that phase's Goal, Tasks and Done when from the roadmap above, and end
with:
Show me the plan first. Build in small steps. Run the tests after each step.
Explain any hard term in one line. Do not start the next phase.

Extra lines to add for the tricky phases:
Phase 4: "Build a fake phone menu I can test against before calling real numbers."
Phase 5: "Before each real call, show me the full plan and wait for my OK."
Phase 7: "Write the safety tests first, then the code. Try hard to break our own rules."
Phase 9: "Explain each ML step like I'm learning it. Show baseline vs our model in a
table."

Review prompt (end of every phase)
Review the current phase against its Done-when list in this message:
[paste the Done-when list]
For each item: done, partly done, or missing — with proof (a test name,
a file, or a command I can run). Then list the 3 weakest parts of what we
built and how to fix them. Do not write new code yet.

Safety and legal rules
This app talks to companies with the user's private details. One mistake can cost
someone money. These rules are not optional.
Never shared, ever: UPI PIN, card number, CVV, passwords, and any OTP that approves a
payment.
Always honest: every call starts with the AI saying it is an AI assistant calling for the user.
Pretending to be the user is wrong and can get the app banned.
Only official contacts: every number and email comes from the company's own website,
with the link saved.

Nivaran — AI Customer Care Agent: Project Plan

The user is in control: the user approves every email, can listen to every call, and can stop
anything anytime.
Privacy: private details are stored encrypted and deleted when the user asks.
Open questions to check before public launch (rules change, so check the current
versions):
Rules on recording phone calls and telling the other side
Telecom (TRAI) rules for automated outgoing calls
India's data protection law (DPDP Act) — what consent you need
Play Store rules for reading notifications (needed for OTP Layer 1)

When to start applying for internships
Start applying after Phase 5 (about week 8). Don't wait for the full app.
By then you have a real recording of the AI solving a real problem with a real company.
That one clip is stronger than most student portfolios. Keep building while you wait for
replies, and send updates as new phases finish.
Who to send it to:
Voice AI and agent startups — this is exactly their work
Indian-language AI companies — your multilingual calls show their use case
Customer-support software companies — you've built the other side of their product
Big tech (Google, Microsoft, Amazon, Samsung) — on-device and agent work is a hot
area
Your resume line (fill the numbers in Phase 10): "Built Nivaran, an AI agent that calls
customer care in X Indian languages; handled Y real cases for Z users with a W% success
rate."

Future scope
"Find it for me" mode (for elders and non-tech users)
The problem: Many older people don't know where to find an order ID, booking number or
bill. So they can't even start a complaint.
The idea: The user just says, "The mixer I ordered last week from Amazon is broken." The
app finds the order by itself and shares the needed details with the company.
How it can find the details, from easiest to hardest:

Nivaran — AI Customer Care Agent: Project Plan

1. Read order emails and SMS (do this first). Almost every order sends a confirmation
email or SMS with the order ID, date and amount. With permission, the app searches
these. It's safer and much more reliable.
2. Open the company's app and look (later). The app opens Amazon, goes to "My
Orders" and finds the matching item, like a human would. This uses Android's
accessibility feature (a tool that lets one app read and tap on another app's screen). It
is powerful but fragile: if Amazon changes its screens, it breaks. Play Store rules for this
feature are also strict, so check them first.
Safety rules for this mode:
The app shows what it found ("Is this the order? Prestige mixer, ₹2,499, 4 Oct") and
waits for a yes.
It only reads. It never buys, cancels, pays or changes anything in another app.
It shares only what the complaint needs (order ID, date, item), nothing more.

Family confirmation (son or daughter approves)
The problem: An elderly user may not understand a question from the agent, may miss an
OTP, or may feel unsure about sharing details. Today they wait for a child to come home
and help.
The idea: The user links one or two trusted family members (a son, daughter or anyone
they choose). When the app needs a confirmation, it can ask them instead.
When the app asks family:
The elder doesn't answer a confirmation within a set time (for example, 2 minutes).
The elder taps "Ask my son/daughter".
The step is sensitive: sharing an OTP, sending a complaint email, or confirming which
order it is.
How it works:
1. The family member gets a notification: "Amma's complaint to Amazon needs your OK. Is
this the right order? Prestige mixer, ₹2,499, 4 Oct."
2. They tap Approve, Reject, or Call Amma.
3. If they approve, the AI continues the call or sends the email. The elder sees what was
approved.
4. If no one responds, the AI pauses safely and retries later (OTP Layer 4).
Safety rules for family confirmation:
The elder decides. Only the elder can add or remove a family member.
Family sees only what is needed to approve that one step, not the whole account.

Nivaran — AI Customer Care Agent: Project Plan

Payment OTPs, UPI PIN and card details are still never shared, even with family
approval.
Every approval is logged: who approved, what, and when.


