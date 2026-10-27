# Phase 4 notes: first phone call (status: PARTIAL, not tagged yet)

## Summary (5 lines)
- Built: the AI "caller" brain (fixed AI disclosure first, never gives or accepts card numbers/OTPs/PINs, only uses facts the user gave, presses keypad buttons, waits on hold, follows the agent's language), Twilio dialer with a one-number allow-list, phone audio pipeline, hold-music detection, keypad tones, encrypted transcripts, Stop/mute/type-to-say control page, browser practice mode with phone-quality sound.
- Practice result: 9 of 10 practice calls handled well (browser path, computer-voice agent); the fake menu was passed every time.
- NOT done: a real phone call. Twilio accepted two calls to the founder's phone (trial number as caller ID) but ended them after 3-6 seconds and never opened the audio connection to us; reason not seen (Twilio's error log page would not load). The founder's networks blocked or dropped the tunnel repeatedly; the founder chose to skip the real call for now.
- Learned: free Twilio trial accounts cannot send call instructions inline, cannot use a friend's number as caller ID (they need the assigned trial number), and cannot change India permission.
- Speed: Groq's free Whisper hears an English phone-quality line in about 0.3 s; the full answer starts 2-4 s after the agent stops; the local model is 6-22 s.

## Done-when check
| Item | Status | Proof |
|---|---|---|
| 10 test calls with a friend, at least 8 handled well | **Partial** | 10 practice calls, 9 handled well (`docs/phase4-practice-results.md`); zero real phone calls, no friend |
| The AI gets through the fake menu every time | **Done in practice** | calls 2, 3, 4 in all three series pressed the right key (tones decoded through phone encoding in `scripts/fake_company_call.py`) |
| Starts every call by saying it is an AI assistant | **Done** | fixed text, tests in all 4 languages, every practice call |
| Hold music: wait quietly | **Done in practice** | `app/voice/hold.py`, call 5; real music not tested |
| Full transcript of every call | **Done** | encrypted text, secrets removed (`app/voice/transcripts.py`), no audio stored |
| "Join call" button | **Partial** | control page: hang up, mute the AI, type a line for it to say. Joining by voice would need a different call setup |
| Real call to a real phone | **Missing** | see summary |

## 3 weakest parts
1. **No real call yet.** Unknown why Twilio dropped the answered calls; the line test (`phone_session.py call --say`) is built to tell a Twilio problem from a streaming problem, but needs a network that holds a tunnel. Next: line test, then the real call; check Twilio's error log.
2. **Speed and hearing.** 2-4 s per answer at best (English, Groq); Hindi/Hinglish need the slow local model or paid Sarvam (about Rs 22 left, paused below Rs 15); the first menu option was once missed by speech-to-text.
3. **Hindi script and test realism.** The AI answers Hindi in English letters when the hearing model writes it that way; all practice agents were computer voices in quiet rooms.

## Demo clip (30 seconds)
Open `/phone/browser`, you play the agent: the AI introduces itself as an AI assistant, you read a menu and it presses the right key (you hear the tone), you say "please hold" and stay silent (it waits), you ask for the OTP (it refuses), you give a ticket number (it says goodbye and hangs up).

## Credits
Sarvam about Rs 22.4 left (estimate). Groq and Gemini free tiers; the Mac voice is free. Twilio trial: 75 free minutes, about 20 days left.
