# Phase 3 notes: voice in the browser

## Summary (5 lines)
- Built: a voice page (`/voice`, Chrome) on Pipecat. Mic -> voice detector -> Sarvam speech-to-text -> brain -> text-to-speech -> speaker. The transport is swappable (browser now, phone line in Phase 4).
- Brain: Groq (free, ~1.5 s per answer) with Gemini as automatic backup; ONE AI call per turn; our own code adds the "how I can contact them / nothing sent yet" sentence.
- Languages: English, Hindi, Tamil, Hinglish, and the bot follows the user when they switch language mid-chat (hearing always auto-detects; the page language is only the starting language).
- Voices: founder's picks are English = Gemini, Hindi/Tamil/Hinglish = Sarvam; the other provider is the automatic backup (a failed voice is skipped for 5 min).
- Safety: spoken card numbers are removed before the AI sees them; the bot never goes silent (spoken apology in the user's language if the brain fails or takes over 20 s).

## Done-when check
| Item | Status | Proof |
|---|---|---|
| A full conversation works in all 4 languages | **Done, with a limit** | `docs/results/voice-live-test.md`: English, Hinglish, Hindi, Tamil each heard right and answered right over real WebRTC. Founder chatted live and switched English -> Hindi; Tamil start -> English worked after a fix. The founder cannot speak Tamil, so Tamil was tested only with a computer voice. Hindi and Tamil fixed sentences were written by Claude and are not yet checked by native speakers. |
| Interrupt the AI mid-sentence; it stops and listens | **Done** | Scenario 5 (speech starts while the greeting plays): greeting stops, answer comes. The unfinished answer is no longer lost when interrupted. |
| Reply delay measured and written down | **Done (goal missed, as a goal)** | End of speech to first sound of the ANSWER, Sarvam voice: Hinglish 3.4 s, Hindi 3.6 s, Tamil 5.0 s, English 4.7 s (7.2 s on the final two-sentence answer). Target was ~1.5 s: not met. Before the fixes it was 15-30 s. Brain part is now ~1.5 s; the rest is voice detection (0.5 s), speech-to-text (0.4-1 s), voice (1-2 s), network. |
| New-clips test (holdout) | **Done** | `docs/results/holdout-result.md`: Sarvam average WER 0.05, Gemini 0.42 (Gemini is partly unfairly penalised for writing Hindi in English letters). Numbers and company names right in nearly all variants. Reference text was first drafted by Sarvam then corrected by the founder, so Sarvam may look slightly better; noise is artificial. |
| Tagged `phase-3-done` | Done | tag pushed |

## 3 weakest parts
1. **Speed.** 3-5 s, not 1.5 s. The AI answer is not streamed word by word; only whole sentences. Free tiers (Groq, Gemini) can be slow or fail at any time; the Gemini voice was down on 23 Oct and needed a 5-minute skip rule. Next: stream the AI answer, start the voice sooner, test the paid or own models in Phase 9.
2. **Language quality is unchecked by native speakers.** Tamil never tested with a real Tamil speaker; fixed Hindi/Tamil sentences are Claude's own. Hindi spoken in English letters is answered in Hinglish. Next: Phase 3.5 with the founder's college speakers.
3. **Little real-world test data.** Holdout is 4 clips, one voice, artificial noise; the brain sometimes picks a different category for the same message (Zomato once "ecommerce" in 7 runs); free-tier limits and daily quotas can stop the bot (Gemini hit its daily limit once). Next: bigger test set in Phase 9, real phone-line audio in Phase 4.

## Credits (honest)
Sarvam: about Rs 37 left of Rs 100 (our own estimate). Groq and Gemini are free tiers; free-tier prompts may be used by the provider, so test data only.

## Demo clip (30 seconds)
Open `/voice` in Chrome. Say in English: "My Swiggy order came cold, I want a refund." The bot asks for the order ID. Answer in Hindi. Show the bot switching to Hindi and saying what it understood and that nothing has been sent. Then say a card number out loud and show "[CARD NUMBER REMOVED]" in the log. Interrupt the bot once.

## Not in this phase
Phase 3.5: Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati, Punjabi (text first, then speech, checked by native speakers). Later: contact picker must understand problem types before Phase 5. Founder to send the GitHub Support message (`docs/archive/github-support-request.md`).
