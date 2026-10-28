# Speech bake-off (Phase 3)

- Date: 2026-10-19; speech-to-text `sarvam:saaras:v3`; text-to-speech `gemini:gemini-3.8-flash-tts` (voice `Kore`)
- Language hint given to the speech-to-text: YES (the app knows the language the user picked)
- Numbers are WORD ERROR RATE (WER): lower is better, 0% is perfect. Phone 8 kHz = telephone sampling rate. mu-law = 8 kHz squeezed like a real phone line.
- 'Two thousand' and '2000', or 'forty' and '40', count as the same when scoring words; the number check below is strict.

## 1. Real voices, quiet clips (word error rate)

For your own clips the second number ignores extra words you spoke around the sentence (see table 5).

| Voices | Clips | Clean | Phone 8 kHz | Phone mu-law |
|---|---|---|---|---|
| Hinglish (your recordings) | 4 | 92% (sentence inside: 36%) | 92% (sentence inside: 36%) | 83% (sentence inside: 32%) |
| Indian English (your recordings) | 4 | 3% (sentence inside: 3%) | 3% (sentence inside: 3%) | 3% (sentence inside: 3%) |
| Hindi (FLEURS, real voices) | 5 | 3% | 7% | 7% |
| Tamil (FLEURS, real voices) | 5 | 19% | 18% | 18% |
| US English (FLEURS, real voices) | 5 | 5% | 6% | 6% |

## 2. Computer voices (a computer voice reads the sentence, the speech-to-text hears it back)

| Language | Clips | Clean | Phone 8 kHz | Phone mu-law |
|---|---|---|---|---|
| Hinglish | 5 | 9% | 21% | 21% |
| English | 5 | 0% | 0% | 0% |
| Hindi | 5 | 0% | 0% | 0% |
| Tamil | 5 | 15% | 15% | 15% |

## 3. Noisy clips (real voices only, shown separately)

| Voices | Clean | Phone 8 kHz | Phone mu-law | What the noise is |
|---|---|---|---|---|
| Hinglish (your recordings) | 71% | 71% | 71% | your recording with real background noise |
| Indian English (your recordings) | 8% | 8% | 8% | your recording with real background noise |
| Hindi (FLEURS, real voices) | 9% | 9% | 9% | FLEURS clip + synthetic chatter at 10 dB |
| Tamil (FLEURS, real voices) | 29% | 29% | 29% | FLEURS clip + synthetic chatter at 10 dB |
| US English (FLEURS, real voices) | 0% | 0% | 0% | FLEURS clip + synthetic chatter at 10 dB |

## 4. One score per language: 70% real voices + 30% computer voices (quiet clips)

| Language | Clean | Phone 8 kHz | Phone mu-law |
|---|---|---|---|
| Hinglish | 67% | 71% | 64% |
| Indian English | 2% | 2% | 2% |
| Hindi | 2% | 5% | 5% |
| Tamil | 18% | 17% | 17% |

## 5. Your own clips, one by one (WER, and WER of the sentence found inside what was heard)

The second number ignores extra words spoken before or after the sentence (for example 'Hello, haan ji...'). A big gap means you said more than the listed sentence, not that the speech-to-text was wrong.

| Clip | Noise | Clean | Phone 8 kHz | Phone mu-law | Heard (clean) |
|---|---|---|---|---|---|
| english-01 |  | 6% / 6% | 6% / 6% | 6% / 6% | My Zomato order came 40 minutes late and the food was cold and I want a refund. |
| english-02 |  | 0% / 0% | 0% / 0% | 0% / 0% | My laptop charger stopped working and it is still under warranty |
| english-03 |  | 0% / 0% | 0% / 0% | 0% / 0% | I paid 2000 rupees through PhonePe, but the money did not reach the other person. |
| english-04 |  | 8% / 8% | 8% / 8% | 8% / 8% | My Indigo flight cancelled and they have not refunded my ticket yet. |
| english-05 | noisy | 8% / 0% | 8% / 0% | 8% / 0% | Hello, my Airtel broadband is not working since yesterday. Please get it fixed. |
| hinglish-01 |  | 100% / 13% | 100% / 13% | 100% / 13% | Hello haan ji toh mera complaint tha ki mera Swiggy ka order ek ghante late aaya aur khana |
| hinglish-02 |  | 100% / 21% | 100% / 14% | 100% / 14% | Gaya? Aa toh bhaga ke phone kiya tha tension ho gaya kya tension hua tha? Maine Jio ka 299 |
| hinglish-03 |  | 100% / 71% | 100% / 71% | 100% / 71% | Hello maine UPL se apne dost ko pandrah sau rupaye bheje the jismein se paise cut gaye hai |
| hinglish-04 |  | 69% / 38% | 69% / 46% | 31% / 31% | Mera order number naal sau aath teen nau do sau ek hai Amazon mein galat size ki kurti bhe |
| hinglish-05 | noisy | 71% / 50% | 71% / 64% | 71% / 64% | Maine IRS shooting se ticket cancel kiya tha 10 din pehle. Tab tak mujhe uska refund nahi  |

## 5b. Does phone quality change what is heard? (your clips: how different is the phone transcript from the clean one)

This needs no ground truth, so it is fair even for clips where you did not read the listed sentence word for word.

| Clip | Phone 8 kHz differs from clean by | Phone mu-law differs from clean by |
|---|---|---|
| english-01 | 0% | 0% |
| english-02 | 0% | 0% |
| english-03 | 0% | 0% |
| english-04 | 0% | 0% |
| english-05 | 0% | 0% |
| hinglish-01 | 0% | 0% |
| hinglish-02 | 14% | 11% |
| hinglish-03 | 4% | 4% |
| hinglish-04 | 20% | 45% |
| hinglish-05 | 39% | 39% |
| **average** | **8%** | **10%** |

## 6. Numbers heard exactly right?

| Clip | Source | Expected | Clean | Phone 8 kHz | Phone mu-law |
|---|---|---|---|---|---|
| english-01 | own | 40 | OK | OK | OK |
| english-03 | own | 2000 | OK | OK | OK |
| english-01 | synth | 40 | OK | OK | OK |
| english-03 | synth | 2000 | OK | OK | OK |
| hinglish-02 | own | 299 | OK | OK | OK |
| hinglish-03 | own | 1500 | WRONG: heard no number | WRONG: heard no number | WRONG: heard no number |
| hinglish-04 | own | 4839201 | WRONG: heard no number | WRONG: heard 0 | WRONG: heard 39201 |
| hinglish-02 | synth | 299 | WRONG: heard no number | WRONG: heard no number | WRONG: heard no number |
| hinglish-03 | synth | 1500 | WRONG: heard no number | WRONG: heard no number | WRONG: heard no number |
| hinglish-04 | synth | 4839201 | OK | WRONG: heard no number | WRONG: heard no number |

**16 of 30 number checks passed.** Mistakes: hinglish-03 (own, clean): heard []; hinglish-03 (own, phone_8k): heard []; hinglish-03 (own, phone_mulaw): heard []; hinglish-04 (own, clean): heard []; hinglish-04 (own, phone_8k): heard ['0']; hinglish-04 (own, phone_mulaw): heard ['39201']; hinglish-02 (synth, clean): heard []; hinglish-02 (synth, phone_8k): heard []; hinglish-02 (synth, phone_mulaw): heard []; hinglish-03 (synth, clean): heard []; hinglish-03 (synth, phone_8k): heard []; hinglish-03 (synth, phone_mulaw): heard []; hinglish-04 (synth, phone_8k): heard []; hinglish-04 (synth, phone_mulaw): heard []

## Speed of one speech-to-text call (not streaming): median 2.9s, slowest 3.5s (144 calls)

## Worst 8 real-voice clips (what was said vs what was heard)

| Clip | Condition | WER | Reference | Heard |
|---|---|---|---|---|
| hinglish-03 | clean | 100% | UPI se 1500 rupaye bheje, paise kat gaye par saamne wale ko nahi mile. | Hello maine UPL se apne dost ko pandrah sau rupaye bheje the jismein se paise cut gaye hai |
| hinglish-03 | phone_8k | 100% | UPI se 1500 rupaye bheje, paise kat gaye par saamne wale ko nahi mile. | Hello maine UPI se apne dost ko pandrah sau rupaye bheje the jismein se paise cut gaye hai |
| hinglish-03 | phone_mulaw | 100% | UPI se 1500 rupaye bheje, paise kat gaye par saamne wale ko nahi mile. | Hello maine UPI se apne dost ko pandrah sau rupaye bheje the jismein se paise cut gaye hai |
| hinglish-05 | phone_8k | 71% | Mera IRCTC ticket cancel kiya tha das din pehle, refund abhi tak nahi  | Maine IRS treatment se treatment kiya tha das din pehle. Uska pain jo uska refund nahi aay |
| hinglish-05 | phone_mulaw | 71% | Mera IRCTC ticket cancel kiya tha das din pehle, refund abhi tak nahi  | Maine IRS treatment se treatment kiya tha das din pehle. Uska pain jo uska refund nahi aay |
| hinglish-05 | clean | 71% | Mera IRCTC ticket cancel kiya tha das din pehle, refund abhi tak nahi  | Maine IRS shooting se ticket cancel kiya tha 10 din pehle. Tab tak mujhe uska refund nahi  |
| hinglish-04 | phone_8k | 69% | Mera order number 4839201 hai, Amazon ne galat size ki kurti bhej di. | Mera order number chaar aath teen nau do zero ek hai Amazon mein galat size ki kurti bhej  |
| hinglish-04 | clean | 69% | Mera order number 4839201 hai, Amazon ne galat size ki kurti bhej di. | Mera order number naal sau aath teen nau do sau ek hai Amazon mein galat size ki kurti bhe |
