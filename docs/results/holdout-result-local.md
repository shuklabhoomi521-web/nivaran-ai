# New-clips (holdout) test

Run once on 2026-10-23 with frozen settings, language = auto. Reference text = what the founder confirmed they said. The first draft of the reference came from Sarvam (founder corrected it), so Sarvam may look slightly better than it is. Noise is artificial (traffic rumble, horns, market babble), not a real street.

| Clip | Condition | Provider | WER | CER | Numbers right | Company right | Problem |
|---|---|---|---|---|---|---|---|
| 1 | clean | Local Hindi2Hinglish | 0.24 | 0.20 | 2/2 | 1/1 |  |
| 1 | noisy 8 dB | Local Hindi2Hinglish | 0.27 | 0.23 | 2/2 | 1/1 |  |
| 1 | phone mu-law | Local Hindi2Hinglish | 0.27 | 0.23 | 2/2 | 1/1 |  |
| 2 | clean | Local Hindi2Hinglish | 0.68 | 0.66 | 2/2 | 1/1 |  |
| 2 | noisy 8 dB | Local Hindi2Hinglish | 0.68 | 0.66 | 2/2 | 1/1 |  |
| 2 | phone mu-law | Local Hindi2Hinglish | 0.68 | 0.66 | 2/2 | 1/1 |  |
| 3 | clean | Local Hindi2Hinglish | 0.74 | 0.76 | 1/1 | 1/1 |  |
| 3 | noisy 8 dB | Local Hindi2Hinglish | 0.74 | 0.77 | 1/1 | 1/1 |  |
| 3 | phone mu-law | Local Hindi2Hinglish | 0.75 | 0.77 | 1/1 | 1/1 |  |
| 4 | clean | Local Hindi2Hinglish | 0.11 | 0.02 | 0/1 | 1/1 |  |
| 4 | noisy 8 dB | Local Hindi2Hinglish | 0.12 | 0.04 | 0/1 | 1/1 |  |
| 4 | phone mu-law | Local Hindi2Hinglish | 0.10 | 0.02 | 0/1 | 1/1 |  |

**Local Hindi2Hinglish average WER: 0.45** over 12 variants
