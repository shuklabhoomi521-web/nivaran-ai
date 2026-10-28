# Speech bake-off (Phase 3)

- Date: 2026-10-24; speech-to-text `local:gemini-3.5-transcribe`; text-to-speech `gemini:gemini-3.8-flash-lite-tts` (voice `Kore`)
- Language hint given to the speech-to-text: YES (the app knows the language the user picked)
- Numbers are WORD ERROR RATE (WER): lower is better, 0% is perfect. Phone 8 kHz = telephone sampling rate. mu-law = 8 kHz squeezed like a real phone line.
- 'Two thousand' and '2000', or 'forty' and '40', count as the same when scoring words; the number check below is strict.

## 1. Real voices, quiet clips (word error rate)

For your own clips the second number ignores extra words you spoke around the sentence (see table 5).

| Voices | Clips | Clean | Phone 8 kHz | Phone mu-law |
|---|---|---|---|---|
| Hinglish (your recordings) | 4 | 85% (sentence inside: 41%) | 87% (sentence inside: 43%) | 87% (sentence inside: 43%) |
| Indian English (your recordings) | 4 | 5% (sentence inside: 5%) | 7% (sentence inside: 7%) | 5% (sentence inside: 5%) |

## 2. Computer voices (a computer voice reads the sentence, the speech-to-text hears it back)

| Language | Clips | Clean | Phone 8 kHz | Phone mu-law |
|---|---|---|---|---|

## 3. Noisy clips (real voices only, shown separately)

| Voices | Clean | Phone 8 kHz | Phone mu-law | What the noise is |
|---|---|---|---|---|
| Hinglish (your recordings) | 100% | 100% | 100% | your recording with real background noise |
| Indian English (your recordings) | 25% | 33% | 33% | your recording with real background noise |

## 4. One score per language: 70% real voices + 30% computer voices (quiet clips)

| Language | Clean | Phone 8 kHz | Phone mu-law |
|---|---|---|---|
| Hinglish | - | - | - |
| Indian English | - | - | - |
| Hindi | - | - | - |
| Tamil | - | - | - |

## 5. Your own clips, one by one (WER, and WER of the sentence found inside what was heard)

The second number ignores extra words spoken before or after the sentence (for example 'Hello, haan ji...'). A big gap means you said more than the listed sentence, not that the speech-to-text was wrong.

| Clip | Noise | Clean | Phone 8 kHz | Phone mu-law | Heard (clean) |
|---|---|---|---|---|---|
| hinglish-01 |  | 100% / 20% | 100% / 20% | 100% / 20% | Hello. Haan ji. To mera complaint tha ki mera Swiggy ka order ek ghante late aaya aur khaa |
| hinglish-02 |  | 100% / 29% | 100% / 29% | 100% / 29% | Hello. Kya to tension ho gaya? Kya tension hua tha? Mainne Jio ka 299 vaala recharge kiya  |
| hinglish-03 |  | 100% / 79% | 100% / 79% | 100% / 79% | Hello. Mainne UPI se apne dost ko pandrah sau rupe bheje the, jismen se paise cut gae hain |
| hinglish-04 |  | 38% / 38% | 46% / 46% | 46% / 46% | Mera order number 4 3 9 2 0 1 hai. Amazon mein galat size ki ghutti bhejti hai. |
| hinglish-05 | noisy | 100% / 100% | 100% / 100% | 100% / 100% | nan |
| english-01 |  | 6% / 6% | 12% / 12% | 6% / 6% | My Zomato order came 40 minutes late and the food was cold and I want a refund. |
| english-02 |  | 0% / 0% | 0% / 0% | 0% / 0% | My laptop charger stopped working and it is still under warranty. |
| english-03 |  | 7% / 7% | 7% / 7% | 7% / 7% | I paid two thousand rupees through through PhonePe but the money did not reach the other p |
| english-04 |  | 8% / 8% | 8% / 8% | 8% / 8% | My Indigo flight cancelled and they have not refunded my ticket yet. |
| english-05 | noisy | 25% / 17% | 33% / 25% | 33% / 25% | Hello, my Airtel booth band is not working since yesterday. Please get it fixed. |

## 5b. Does phone quality change what is heard? (your clips: how different is the phone transcript from the clean one)

This needs no ground truth, so it is fair even for clips where you did not read the listed sentence word for word.

| Clip | Phone 8 kHz differs from clean by | Phone mu-law differs from clean by |
|---|---|---|
| hinglish-01 | 0% | 0% |
| hinglish-02 | 0% | 0% |
| hinglish-03 | 4% | 8% |
| hinglish-04 | 15% | 15% |
| hinglish-05 | 0% | 0% |
| english-01 | 6% | 0% |
| english-02 | 0% | 0% |
| english-03 | 0% | 0% |
| english-04 | 0% | 0% |
| english-05 | 7% | 7% |
| **average** | **3%** | **3%** |

## 6. Numbers heard exactly right?

| Clip | Source | Expected | Clean | Phone 8 kHz | Phone mu-law |
|---|---|---|---|---|---|
| hinglish-02 | own | 299 | OK | OK | OK |
| hinglish-03 | own | 1500 | WRONG: heard no number | WRONG: heard no number | WRONG: heard no number |
| hinglish-04 | own | 4839201 | WRONG: heard 439201 | WRONG: heard 439201, 5 | WRONG: heard 439201, 5 |
| english-01 | own | 40 | OK | OK | OK |
| english-03 | own | 2000 | OK | OK | OK |

**9 of 15 number checks passed.** Mistakes: hinglish-03 (own, clean): heard []; hinglish-03 (own, phone_8k): heard []; hinglish-03 (own, phone_mulaw): heard []; hinglish-04 (own, clean): heard ['439201']; hinglish-04 (own, phone_8k): heard ['439201', '5']; hinglish-04 (own, phone_mulaw): heard ['439201', '5']

## Speed of one speech-to-text call (not streaming): median 3.1s, slowest 25.0s (30 calls)

## Worst 8 real-voice clips (what was said vs what was heard)

| Clip | Condition | WER | Reference | Heard |
|---|---|---|---|---|
| hinglish-05 | clean | 100% | Mera IRCTC ticket cancel kiya tha das din pehle, refund abhi tak nahi  | nan |
| hinglish-05 | phone_8k | 100% | Mera IRCTC ticket cancel kiya tha das din pehle, refund abhi tak nahi  | nan |
| hinglish-05 | phone_mulaw | 100% | Mera IRCTC ticket cancel kiya tha das din pehle, refund abhi tak nahi  | nan |
| hinglish-03 | clean | 100% | UPI se 1500 rupaye bheje, paise kat gaye par saamne wale ko nahi mile. | Hello. Mainne UPI se apne dost ko pandrah sau rupe bheje the, jismen se paise cut gae hain |
| hinglish-03 | phone_8k | 100% | UPI se 1500 rupaye bheje, paise kat gaye par saamne wale ko nahi mile. | Hello. Mainne UTI se apne dost ko pandrah sau rupe bheje the, jismen se paise cut gae hain |
| hinglish-03 | phone_mulaw | 100% | UPI se 1500 rupaye bheje, paise kat gaye par saamne wale ko nahi mile. | Hello. Mainne UTI se apne dost ko pandrah sau rupe bheje the, jismen se paise cut gae hain |
| hinglish-04 | phone_8k | 46% | Mera order number 4839201 hai, Amazon ne galat size ki kurti bhej di. | Mera order number 4 3 9 2 0 1 hai. Amazon mein galat 5 ki karti bhejti hai. |
| hinglish-04 | phone_mulaw | 46% | Mera order number 4839201 hai, Amazon ne galat size ki kurti bhej di. | Mera order number 4 3 9 2 0 1 hai. Amazon mein galat 5 ki karti bhejti hai. |
