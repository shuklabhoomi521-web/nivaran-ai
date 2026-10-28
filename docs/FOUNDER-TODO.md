# Founder to-do list (kept by Claude; shown only when you ask for "the list")

Last updated: 2026-10-27

## Waiting for you
1. **Send the GitHub Support message** (text in `docs/archive/github-support-request.md`). It asks GitHub to clean up old cached files after the recordings purge. Do not create a new repo.
2. **Exotel reply.** Tell me when Exotel answers about KYC with a Udyam registration (needed before Phase 5 real company calls). I record it in `docs/TODO-research.md`.
3. **The first real Twilio phone call (skipped for now, your decision on 2026-10-27).** When you want it:
   - be on a network that holds the tunnel (run `python scripts/phone_session.py check` first; other Wi-Fi or another phone's hotspot);
   - tell me "go": I start the tunnel and the voice bot, do the **line test first** (the phone just speaks one sentence), then the real call;
   - keep the phone in your hand, answer at once, and press any key when Twilio's trial message starts.
   - Twilio trial facts: 75 free voice minutes, 30 days from 2026-10-24 (ends about 2026-11-23). The "From" number is the trial number from the Try out Voice page. Only your own number can be called.
4. **India calling permission** on Twilio cannot be changed on a trial account (page asks for upgrade). We only find out at the first real call. Do not pay or upgrade.
5. **Native speakers** (Hindi and Tamil) should check the fixed sentences the bot says (Phase 3.5, with your college friends). I wrote them myself.
6. **Sarvam credit:** about Rs 32.8 left (my own estimate; compare with the Sarvam dashboard now and then). I pause Sarvam below Rs 15 and ask you first.
7. **Decide** whether Phase 4 is tagged as "partial" (see `docs/notes/phase-4.md` when I write it).

## Waiting for a better moment (not urgent)
- Friend joins a practice call from their own browser: needs the tunnel on a good network (the browser practice page is `/phone/browser`).
- Phase 3.5: Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati, Punjabi (after Phase 5).
- Before Phase 5: contact picker must understand problem types (`docs/TODO-research.md`); TRAI rules research.
- Phase 9: bigger test set and own models.

## Decisions already made (so I do not ask again)
- Free tools first. Local free speech model (`STT_PROVIDER=local`) for development; Groq's free Whisper for English practice calls; Sarvam only for real calls and the final demo.
- Shruti (needs a third-party engine program): skipped.
- The first real call to be placed only when you say so.
