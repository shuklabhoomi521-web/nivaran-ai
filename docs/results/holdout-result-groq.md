# New-clips (holdout) test

Run once on 2026-10-23 with frozen settings, language = auto. Reference text = what the founder confirmed they said. The first draft of the reference came from Sarvam (founder corrected it), so Sarvam may look slightly better than it is. Noise is artificial (traffic rumble, horns, market babble), not a real street.

| Clip | Condition | Provider | WER | CER | Numbers right | Company right | Problem |
|---|---|---|---|---|---|---|---|
| 1 | clean | Groq Whisper | 0.33 | 0.35 | 2/2 | 1/1 |  |
| 1 | noisy 8 dB | Groq Whisper | 0.33 | 0.35 | 2/2 | 1/1 |  |
| 1 | phone mu-law | Groq Whisper | 0.33 | 0.35 | 2/2 | 1/1 |  |
| 2 | clean | Groq Whisper | 0.86 | 0.78 | 2/2 | 1/1 |  |
| 2 | noisy 8 dB | Groq Whisper | 0.82 | 0.69 | 2/2 | 1/1 |  |
| 2 | phone mu-law | Groq Whisper | 0.86 | 0.78 | 2/2 | 1/1 |  |
| 3 | clean | Groq Whisper | 0.83 | 0.73 | 1/1 | 1/1 |  |
| 3 | noisy 8 dB | Groq Whisper | 0.82 | 0.74 | 1/1 | 1/1 |  |
| 3 | phone mu-law | Groq Whisper | 0.84 | 0.74 | 1/1 | 1/1 |  |
| 4 | clean | Groq Whisper | 0.01 | 0.01 | 1/1 | 1/1 |  |
| 4 | noisy 8 dB | Groq Whisper | 0.07 | 0.06 | 1/1 | 1/1 |  |
| 4 | phone mu-law | Groq Whisper | 0.01 | 0.01 | 1/1 | 1/1 |  |

**Groq Whisper average WER: 0.51** over 12 variants
