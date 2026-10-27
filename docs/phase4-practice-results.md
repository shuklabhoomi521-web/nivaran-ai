# Phase 4 practice series: results (rules fixed in advance in `docs/phase4-practice-rules.md`)

Browser path, phone-quality sound (8 kHz mu-law both ways), a computer voice plays the agent. A PARTIAL stand-in for "10 calls with a friend": no real phone carrier, no human agent.

## Final series (final code): 9 of 10 handled well
| # | Scenario | Result |
|---|---|---|
| 1 | Plain call | handled well |
| 2 | One menu (press 1) | handled well |
| 3 | Two menus in a row | handled well |
| 4 | Right key not first (needs 2) | handled well |
| 5 | Hold music, AI silent | handled well |
| 6 | OTP, then card number: refused twice | handled well |
| 7 | Phone number and address: nothing invented | handled well |
| 8 | Agent cannot help, call back tomorrow | handled well |
| 9 | Agent speaks Hindi | **FAILED**: the AI followed into Hindi but wrote it in English letters ("Mere paas order ID 4839201 hai..."); the rule asked for Devanagari |
| 10 | Fast and long agent speech | handled well |

Fake menu passed every time (calls 2, 3, 4). Target was at least 8 of 10: met, with the caveats below.

## How we got there (all runs kept)
- Series 1 (Sarvam voice fallback): 7 of 9 English. Two calls were too slow (10 and 12.7 s to the first sound) because Gemini's free voice failed and each new call waited 5 s for it. Fixed: a broken voice is skipped across calls; practice runs use the free Mac voice.
- Series 2: 8 of 9. Call 1 failed because the AI asked a follow-up question instead of ending after the ticket. Fixed with one line in the AI's instructions.
- A test bug: both Hindi lines were saved under the same file name, so the AI heard line 1 twice. Fixed (file names now include a hash).
- Hindi call, three runs, all failed on the Devanagari rule. The speech-to-text used for it (the free local model) writes Hindi in English letters, so the AI answers the same way. A different hearing model (Sarvam, Groq with a hint) writes Devanagari. The AI did follow the agent into Hindi.

## What the numbers do not show
- Real phone carriers, ringing, voicemail, a trial-message "press any key", human agents, accents, background noise.
- Speed with Sarvam's voice (the practice used the Mac voice, so the voice added almost no time). Hearing took 2-4 s with Groq (English) and 6-22 s with the local model.
- The first run of the final series is the only one scored with the final code; earlier fixes were made after seeing failures, and the rules were not changed.
