# Nivaran: technical write-up

*An AI customer-care agent for India. About 2 pages. Every number here is measured and has a file behind it in `docs/results/`. Status words are literal: "partial" means partial.*

## 1. The problem

In India, fixing a problem with a company often means finding the right helpline, waiting on hold, explaining the issue again in a language the agent may not speak, and then having nobody follow up. Some big apps (Swiggy, Zomato, Zepto) officially have no customer phone line, so the right step is a grievance email. Fake "customer care" numbers found through web search make this worse.

**Goal:** the user states the problem once, in their own language. The agent finds the *official* contact, speaks for the user (call or email), and never touches an OTP, PIN or card.

## 2. Approach

Four design choices shaped everything.

1. **A verified directory, not web search.** Search results (and AI summaries of them) were wrong or stale in Phase 2: a BSNL page that no longer exists, look-alike "care" sites. Each contact is stored with the official source link, an exact quote and a checked-on date. This is slower to build and safe to act on.
2. **Safety in code, not in prompts.** Secrets are removed before any AI sees the text. The OTP/card/PIN refusal and the AI-disclosure sentence ("I am an AI assistant calling on behalf of a customer...") are decided by code and are fixed text in four languages. An AI model can be talked out of a rule. A code check cannot.
3. **Free tiers first.** The founder is a student with no budget. The brain is Groq (free) with Gemini as an automatic backup. Hindi hearing uses a local open model. Mac voices are used in development. The price is speed and flakiness, so every call to an outside service has a timeout and a backup.
4. **Everything swappable.** Speech providers, the brain and the phone provider sit behind small interfaces, so a paid or self-trained model can replace any one of them later without touching the rest.

## 3. Architecture

Audio comes in from a browser (WebRTC) or a phone line (Twilio Media Streams) into one **Pipecat** pipeline: voice-activity detection, interruption handling, hold-music detection, and DTMF (keypad tone) generation and decoding. Speech-to-text (Sarvam, local Whisper, Groq Whisper, Gemini) feeds an input safety guard, then the **brain**: one AI call per turn that returns structured JSON. The reply is streamed, so the first sentence is spoken while the rest is still being written. An output guard checks every sentence, and text-to-speech (Sarvam, Gemini or a Mac voice) plays it. The brain reads company contacts only from the verified directory (40 companies, 10 categories). The diagram is in the README.

The call brain has a few details that mattered in practice. The JSON field order is `action`, `digits`, `reply_language`, `say`, so the model decides what to do before it starts talking. The reply language is detected in code from the script and common words, so Hindi is answered in Devanagari (or Hinglish if the setting says so). Calls are limited to one allowed phone number, need an explicit user OK, and can be hung up or muted at any time.

## 4. How we evaluated

- **Understanding (Phase 1):** 30 test problems in English, Hindi, Tamil and Hinglish. Check: the right company, category and goal, with facts copied exactly and nothing invented.
- **Directory (Phase 2):** every contact needs an official source link and a quote. We re-checked contacts against saved pages.
- **Speech (Phase 3):** a bake-off, then a **holdout test**: 4 new recorded clips never used for tuning, each in 3 variants (clean, 8 dB artificial street noise, simulated phone line), so 12 in total. The metric is word error rate (WER): lower is better.
- **Phone calls (Phase 4):** 10 practice calls. The pass rules (P1-P5 plus an expected result for each scenario) were **written before running them**, and every run, including failures, is kept.

## 5. Results

| What | Result | Limit |
|---|---|---|
| Understanding, 30 problems | **28/30 (93%)** strict on a full re-run; 30/30 under a later meaning-based rule on the same answers | Small set, mostly written by us. The relaxed rule was chosen *after* seeing the 2 misses. The same prompt can flip a problem between runs. |
| Directory | **40 companies**; 25/25 problems naming a company got a verified contact | Only 10 of 63 phone numbers confirmed on two official pages. Contacts go stale. |
| Hearing, holdout WER | **Sarvam 0.05**, Gemini 0.42, local Hindi2Hinglish 0.45, Groq Whisper 0.51 | 4 clips, one speaker, artificial noise. Spelling a Hindi word in Roman vs Devanagari inflates some scores. |
| Practice calls | **9 of 10 handled well**; every keypad menu passed; every OTP and card request refused | A computer voice plays the company, in the browser. **Zero real company calls.** The failed call (Hindi) was a speed miss. |
| Reply speed | 2-4 s after the other side stops (brain 0.5-1.5 s) | Goal was 1.5 s: **missed**. |
| Tests | 422 free tests on every push (CI); 16 redaction, 31 secret/OTP/card/PIN | They prove the rules in code, not every real-world phrasing. |

**Phase status:** 0, 2, 3 done. Phase 1 partial (28/30). **Phase 4 partial:** the phone layer works with simulated phone-quality audio, but the one real Twilio test call we tried failed. Twilio ended two answered calls after 3-6 seconds without opening the audio stream. We never found the cause, and our networks also dropped the tunnel it needs. Phase 5 onward has not started.

## 6. What I learned

- **Measure before you choose.** The bake-off changed the plan: the cheapest options were worse on Indian-language phone audio by a large margin (0.45-0.51 WER against 0.05).
- **Do not change the rule after the result.** Our meaning-based score (30/30) looks better than the strict one (28/30). Both are reported, and the reason for the difference is written next to them.
- **Phone audio is its own problem.** An 8 kHz mu-law line needs a low-pass filter before downsampling, or the sound aliases. We learned this by building the filter after a first version without one.
- **Free tiers need defensive code.** Gemini voice timeouts made every new call wait 5 s until we added a shared skip timer. Bugs like a greeting played twice (the transport announces one connection twice) only show up in live runs.
- **Honest status is worth more than a big claim.** The weakest part (no real call) is the first thing the README says.

## 7. What's next

1. Find the cause of the dropped Twilio call, with a good network and Twilio's debugger tools.
2. Phase 5: real company calls. That needs KYC with a phone provider, plus research on TRAI rules for automated calls.
3. Phases 6-8: mobile app, safe OTP handling, email with user approval and escalation.
4. Phase 9: train our own open models to replace the outside brain one job at a time, keeping Gemini as the backup until the scores are close.
5. More languages (Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati, Punjabi), a larger and independent test set, and native-speaker checks of the fixed Hindi and Tamil sentences.
