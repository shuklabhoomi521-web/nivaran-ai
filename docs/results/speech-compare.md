# Speech-to-text comparison: A = `gemini_prompt-gemini-3.5-flash-lite-hint`, B = `sarvam-saaras-v4-hinglish=codemix-keyterms-hint`

Word error rate (lower is better). Own clips use 'sentence inside' (extra words you spoke are ignored). Same clips, same language hint.

### Real voices, quiet clips

| Voices | Clean (A / B) | Phone 8 kHz (A / B) | Phone mu-law (A / B) |
|---|---|---|---|
| Hinglish (your recordings) | 30% / 37% | 31% / 37% | 32% / 37% |
| Indian English (your recordings) | 10% / 3% | 7% / 3% | 10% / 3% |
| Hindi (FLEURS) | 21% / 1% | 26% / 1% | 26% / 3% |
| Tamil (FLEURS) | 38% / 18% | 51% / 18% | 31% / 18% |
| US English (FLEURS) | 3% / 4% | 3% / 6% | 5% / 4% |

### Real voices, noisy clips

| Voices | Clean (A / B) | Phone 8 kHz (A / B) | Phone mu-law (A / B) |
|---|---|---|---|
| Hinglish (your recordings) | 71% / 57% | 86% / 57% | 79% / 57% |
| Indian English (your recordings) | 0% / 0% | 0% / 0% | 0% / 0% |
| Hindi (FLEURS) | 18% / 0% | 9% / 0% | 18% / 0% |
| Tamil (FLEURS) | 43% / 43% | 29% / 43% | 29% / 43% |
| US English (FLEURS) | 0% / 0% | 0% / 0% | 0% / 0% |

### Computer voices (round trip)

| Language | Clean (A / B) | Phone 8 kHz (A / B) | Phone mu-law (A / B) |
|---|---|---|---|
| hinglish | 1% / 16% | 4% / 17% | 3% / 17% |
| english | 1% / 0% | 3% / 1% | 4% / 1% |
| hindi | 6% / 0% | 20% / 0% | 8% / 0% |
| tamil | 13% / 0% | 25% / 0% | 10% / 0% |

### Numbers heard exactly right (4839201, 299, 1500, 2000, 40): A 30 of 30, B 30 of 30

### Time for one call, measured separately without our slow-down (5 different 5-8 s phone-quality clips)

Measured on 2026-10-19: Sarvam median 0.3 s (slowest 1.4 s); Gemini lite model median 5.1 s (slowest 8.5 s). Other timings in the run tables include our own wait between calls and are not real call times.
