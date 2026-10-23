# New-clips (holdout) test

Run once on 2026-10-23 with frozen settings, language = auto. Reference text = what the founder confirmed they said. The first draft of the reference came from Sarvam (founder corrected it), so Sarvam may look slightly better than it is. Noise is artificial (traffic rumble, horns, market babble), not a real street.

| Clip | Condition | Provider | WER | CER | Numbers right | Company right | Problem |
|---|---|---|---|---|---|---|---|
| 1 | clean | Sarvam | 0.04 | 0.04 | 2/2 | 1/1 |  |
| 1 | clean | Gemini | 0.65 | 0.54 | 2/2 | 1/1 |  |
| 1 | noisy 8 dB | Sarvam | 0.20 | 0.18 | 2/2 | 1/1 |  |
| 1 | noisy 8 dB | Gemini | 0.59 | 0.53 | 2/2 | 0/1 |  |
| 1 | phone mu-law | Sarvam | 0.27 | 0.22 | 2/2 | 1/1 |  |
| 1 | phone mu-law | Gemini | 0.43 | 0.29 | 2/2 | 1/1 |  |
| 2 | clean | Sarvam | 0.00 | 0.00 | 2/2 | 1/1 |  |
| 2 | clean | Gemini | 0.33 | 0.40 | 2/2 | 1/1 |  |
| 2 | noisy 8 dB | Sarvam | 0.00 | 0.00 | 2/2 | 1/1 |  |
| 2 | noisy 8 dB | Gemini | 0.37 | 0.39 | 2/2 | 1/1 |  |
| 2 | phone mu-law | Sarvam | 0.02 | 0.00 | 2/2 | 1/1 |  |
| 2 | phone mu-law | Gemini | 0.35 | 0.41 | 2/2 | 1/1 |  |
| 3 | clean | Sarvam | 0.01 | 0.01 | 1/1 | 1/1 |  |
| 3 | clean | Gemini | 0.65 | 0.64 | 1/1 | 1/1 |  |
| 3 | noisy 8 dB | Sarvam | 0.01 | 0.01 | 1/1 | 1/1 |  |
| 3 | noisy 8 dB | Gemini | 0.75 | 0.76 | 1/1 | 1/1 |  |
| 3 | phone mu-law | Sarvam | 0.01 | 0.01 | 1/1 | 1/1 |  |
| 3 | phone mu-law | Gemini | 0.82 | 0.76 | 1/1 | 1/1 |  |
| 4 | clean | Sarvam | 0.00 | 0.00 | 1/1 | 1/1 |  |
| 4 | clean | Gemini | 0.02 | 0.01 | 1/1 | 1/1 |  |
| 4 | noisy 8 dB | Sarvam | 0.00 | 0.00 | 1/1 | 1/1 |  |
| 4 | noisy 8 dB | Gemini | 0.07 | 0.04 | 1/1 | 1/1 |  |
| 4 | phone mu-law | Sarvam | 0.01 | 0.01 | 1/1 | 1/1 |  |
| 4 | phone mu-law | Gemini | 0.04 | 0.02 | 1/1 | 1/1 |  |

**Sarvam average WER: 0.05** over 12 variants

**Gemini average WER: 0.42** over 12 variants
