# Free speech-to-text backup for Hinglish and Hindi (2026-10-23)

Why: Sarvam credit is about Rs 36 left; Gemini's speech-to-text is unreliable (hangs, writes Hindi in English letters).

## Groq free Whisper (`whisper-large-v3`, no card): tested, NOT good enough as the Hinglish/Hindi backup
Word error rate, lower is better. Same old clips, language hint given (page language). Sarvam and Gemini numbers are from `docs/speech-compare.md` (sentence-inside score for own clips).

| Voices (quiet clips, clean) | Groq Whisper | Sarvam | Gemini |
|---|---|---|---|
| Hinglish (own, 4 clips) | 61% | 37% | 30% |
| Indian English (own) | 7% | 3% | 10% |
| Hindi (FLEURS) | 20% | 1% | 21% |
| Tamil (FLEURS) | 43% | 18% | 38% |
| US English (FLEURS) | 4% | 4% | 3% |

New holdout clips (language = auto, 12 variants incl. noise and phone line): Groq Whisper average WER **0.51**, Sarvam **0.05**, Gemini **0.42** (`docs/holdout-result*.md`).
- Whisper in auto mode **translated** the Hindi parts into English and dropped words (clips 2 and 3, WER 0.82-0.86). With a hint it writes Hindi in Devanagari, not English letters ("ओडर").
- A hint prompt with an example order number leaked into the output (a made-up "Order ID 4839201" appeared). Fixed by removing the example; the holdout run used the leaky prompt, so treat its Groq number as a lower bound. Not re-tuned on the holdout clips.
- Numbers and company names were still right in most variants. Free limits: 20 requests/minute, 28,800 audio seconds/day (we hit "429 too many requests" at 15/min; 8/min works).
- Verdict: fine for English, usable but weak for Hindi, poor for Hinglish and Tamil. Keep as a last-resort English backup only. It is added as `STT_PROVIDER=groq`.

## Better free candidates (found by search, NOT yet tested; vendor claims only)
- [Whisper-Hindi2Hinglish (Oriserve)](https://huggingface.co/oriserve/whisper-hindi2hinglish-prime): Whisper large-v3 fine-tune that writes Hindi-English speech as Hinglish. Apache 2.0. Runs on our laptop (free, slower; needs a GPU or patience for live use).
- [Shruti (Udgam Labs)](https://huggingface.co/udgamlabs/Shruti): 55M-parameter Hindi/English/Hinglish model that runs offline. Small, so less accurate for pure Hindi.
- [AI4Bharat IndicConformer](https://aikosh.indiaai.gov.in/home/models/details/indic_conformer_model_for_asr.html): Indian-language model, MIT licence on that listing; Hinglish support unverified.
Next step (if the founder agrees, no signup needed): test Hindi2Hinglish and IndicConformer on the same clips. Phase 9 (own models) will use whichever scores best.

## Recommendation
Keep Sarvam as the main ears. Rs 36 is roughly 70 minutes of speech-to-text; careful use is enough for Phase 4 tests. Do not spend credit on dev chats (use recorded clips). Candidate local models are the free backup to evaluate before the credit runs out.
