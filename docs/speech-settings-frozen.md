# Speech settings: frozen on 2026-10-19, and the new-clips test

## Why this file exists
Sarvam's scores in `docs/speech-compare.md` are **optimistic**. We looked at results on the same 38 clips (your 10 recordings,
18 FLEURS clips, 20 computer-voice sentences) and changed Sarvam's settings until it did well on them. That is like practising on
the exam paper. Gemini was tuned much less (only the language hint). Fair comparison needs audio the settings never saw.

## What was tuned on the scored clips (so the scores are optimistic)
| Setting | What we saw | What we chose |
|---|---|---|
| Model | v3 garbled the noisy IRCTC clip; v4 heard it | `saaras:v4` |
| Hinglish output mode | `translit` wrote numbers as Hindi words ("pandrah sau"); `transcribe` lost a number; `codemix` got all numbers | `codemix` |
| Company-name key terms | with the directory names, IRCTC was spelled right even at phone quality | on (`SARVAM_COMPANY_KEYTERMS=true`) |
| Language hint | without it, Gemini wrote Hindi in English letters and mixed up Tamil | hint = the language the user picked (same for both providers) |

## Frozen from now on
Do not change these before the new-clips test: `SARVAM_STT_MODEL=saaras:v4`, `SARVAM_HINGLISH_MODE=codemix`, `SARVAM_COMPANY_KEYTERMS=true`,
the language-hint mapping in `SarvamSTT.HINTS`, Gemini fallback `gemini_prompt` with `gemini-3.5-flash-lite` and its prompt.
If a setting must change, write the date and reason here and treat the new-clips test as not yet done.

## The new-clips test (to do before Phase 3 is done)
1. The founder writes 5 NEW sentences **before** recording, in `speech_test/holdout/sentences.json` (language, exact text).
   Suggested mix: 2 Hinglish, 1 Indian English, 1 Hindi, 1 Tamil; at least two with a number and two with a company name from the directory; one with background noise.
2. Record them (same as before: any phone format is fine) into `speech_test/holdout/`.
3. Run Sarvam and Gemini on them **once**, clean + 8 kHz + mu-law, with the frozen settings. Report both. No tuning afterwards.
4. Compare with the tuned-clip scores. A big drop means the earlier scores were too rosy.

## Sarvam credit
Tracked by our own ledger (`.sarvam_credits.json`, estimate). See the "Sarvam credit" line at the end of each bake-off report.
At about Rs 25 left it warns, at Rs 10 it warns loudly, below Rs 2 speech goes to the Gemini backup automatically.
