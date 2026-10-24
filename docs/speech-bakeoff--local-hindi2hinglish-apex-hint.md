# Speech bake-off (Phase 3)

- Date: 2026-10-24; speech-to-text `local:gemini-3.5-transcribe`; text-to-speech `gemini:gemini-3.8-flash-lite-tts` (voice `Kore`)
- Language hint given to the speech-to-text: YES (the app knows the language the user picked)
- Numbers are WORD ERROR RATE (WER): lower is better, 0% is perfect. Phone 8 kHz = telephone sampling rate. mu-law = 8 kHz squeezed like a real phone line.
- 'Two thousand' and '2000', or 'forty' and '40', count as the same when scoring words; the number check below is strict.

## 1. Real voices, quiet clips (word error rate)

For your own clips the second number ignores extra words you spoke around the sentence (see table 5).

| Voices | Clips | Clean | Phone 8 kHz | Phone mu-law |
|---|---|---|---|---|
| Hindi (FLEURS, real voices) | 5 | 100% | 100% | 100% |
| US English (FLEURS, real voices) | 5 | 12% | 12% | 10% |

## 2. Computer voices (a computer voice reads the sentence, the speech-to-text hears it back)

| Language | Clips | Clean | Phone 8 kHz | Phone mu-law |
|---|---|---|---|---|

## 3. Noisy clips (real voices only, shown separately)

| Voices | Clean | Phone 8 kHz | Phone mu-law | What the noise is |
|---|---|---|---|---|
| Hindi (FLEURS, real voices) | 100% | 100% | 100% | FLEURS clip + synthetic chatter at 10 dB |
| US English (FLEURS, real voices) | 0% | 6% | 6% | FLEURS clip + synthetic chatter at 10 dB |

## 4. One score per language: 70% real voices + 30% computer voices (quiet clips)

| Language | Clean | Phone 8 kHz | Phone mu-law |
|---|---|---|---|
| Hinglish | - | - | - |
| Indian English | - | - | - |
| Hindi | - | - | - |
| Tamil | - | - | - |

## Speed of one speech-to-text call (not streaming): median 3.3s, slowest 21.1s (36 calls)

## Worst 8 real-voice clips (what was said vs what was heard)

| Clip | Condition | WER | Reference | Heard |
|---|---|---|---|---|
| hindi-fleurs-01 | clean | 100% | अंतरिक्ष में उपग्रह को कॉल मिलता है और फिर इसे वापस नीचे, उसी समय पराव | Antarikshy mein upagrah ko call milta hai aur phir ise vaapas niche usi samay paraavartit  |
| hindi-fleurs-01 | phone_8k | 100% | अंतरिक्ष में उपग्रह को कॉल मिलता है और फिर इसे वापस नीचे, उसी समय पराव | Antarikshy mein upagrah ko call milta hai aur phir ise vaapas niche usi samay paraavartit  |
| hindi-fleurs-01 | phone_mulaw | 100% | अंतरिक्ष में उपग्रह को कॉल मिलता है और फिर इसे वापस नीचे, उसी समय पराव | Antarikshy mein upagrah ko call milta hai aur phir ise vaapas niche usi samay paraavartit  |
| hindi-fleurs-02 | clean | 100% | प्रथम विश्व युद्ध के दौरान युद्ध की भयानकता और अत्याचारों को देखने के  | Pratham vishv ke dauraan yuddh ki bhayaankata aur atyachaaron ko dekhane ke baad raashtrab |
| hindi-fleurs-02 | phone_8k | 100% | प्रथम विश्व युद्ध के दौरान युद्ध की भयानकता और अत्याचारों को देखने के  | Pratham vishv ke dauraan yuddh ki bhayaankata aur atyachaaron ko dekhane ke baad raashtrab |
| hindi-fleurs-02 | phone_mulaw | 100% | प्रथम विश्व युद्ध के दौरान युद्ध की भयानकता और अत्याचारों को देखने के  | Pratham vishv ke dauraan yuddh ki bhayaankata aur atyachaaron ko dekhane ke baad raashtrab |
| hindi-fleurs-03 | clean | 100% | इस सीज़न में बीमारी के शुरुआती मामले जुलाई के आखिर में सामने आए थे. | Is season mein bimaari ke shuruaati maamle July ke aakhir mein saamne aae the. |
| hindi-fleurs-03 | phone_8k | 100% | इस सीज़न में बीमारी के शुरुआती मामले जुलाई के आखिर में सामने आए थे. | Is season mein bimaari ke shuruaati maamle July ke aakhir mein saamne aae the. |
