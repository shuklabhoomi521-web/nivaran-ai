# Phase 3 notes (voice in the browser) — status: IN PROGRESS, not tagged

## Done-when check (live test 2026-10-22, docs/voice-live-test.md)
| Item | Status | Proof |
|---|---|---|
| Hear speech in en/hi/ta/hinglish | done | all 6 scenarios transcribed correctly (Sarvam STT, ~0.4 s) |
| Understand + ask one question | done (4 of 6 scenarios replied with a right question/summary) | live test table |
| Hindi scenario | FAILED this run: heard right, no reply (brain gave no answer in time) | scenario 3 |
| Talking over the bot (barge-in) | done: greeting stopped, answer came | scenario 5 |
| Card number said aloud is removed | done | scenario 6: "[CARD NUMBER REMOVED]" |
| Delay about 1.5 s | MISSED (goal, not pass/fail) | see below |
| Voice choice | waiting for founder | /voice/choice/ |
| 4-language chat by founder | waiting | |
| 5 new holdout clips | waiting | docs/speech-settings-frozen.md |

## Delay (honest)
Table shows ~7.5-7.9 s "to first sound". That sound is the "one moment" filler (it fires at 6 s).
The real answer came after 15-19 s, because the free Gemini text model was slow tonight (6-11 s per tiny call, 503 errors).
Speech-to-text (~0.4 s) and Sarvam voice (~1 s) are fast. The brain is the bottleneck.

## 3 weakest parts
1. Brain speed on the free Gemini tier (two AI calls on the final turn; 15-19 s tonight).
2. Hindi path failed once (no reply); needs retry and a spoken "sorry, say it again" instead of silence.
3. Credit use: Sarvam is about Rs 56 left (estimate); free alternatives not yet researched.

## Demo clip idea (30 s)
Say a Zomato refund problem in Hinglish; bot asks for the order ID; say a card number aloud and show it is removed on screen; interrupt the bot mid-sentence.

## Next
Fixes ideas: one combined AI call, faster model, spoken apology on failure. Phase 9 own models. Then founder items above, then tag phase-3-done.
