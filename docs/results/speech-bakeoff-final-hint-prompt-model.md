# Speech bake-off (Phase 3)

- Date: 2026-10-19; speech-to-text `gemini_prompt:gemini-3.5-flash-lite`; text-to-speech `gemini:gemini-3.8-flash-tts` (voice `Kore`)
- Language hint given to the speech-to-text: YES (the app knows the language the user picked)
- Numbers are WORD ERROR RATE (WER): lower is better, 0% is perfect. Phone 8 kHz = telephone sampling rate. mu-law = 8 kHz squeezed like a real phone line.
- 'Two thousand' and '2000', or 'forty' and '40', count as the same when scoring words; the number check below is strict.

## 1. Real voices, quiet clips (word error rate)

For your own clips the second number ignores extra words you spoke around the sentence (see table 5).

| Voices | Clips | Clean | Phone 8 kHz | Phone mu-law |
|---|---|---|---|---|
| Hinglish (your recordings) | 4 | 77% (sentence inside: 30%) | 83% (sentence inside: 31%) | 83% (sentence inside: 32%) |
| Indian English (your recordings) | 4 | 10% (sentence inside: 10%) | 7% (sentence inside: 7%) | 10% (sentence inside: 10%) |
| Hindi (FLEURS, real voices) | 5 | 21% | 26% | 26% |
| Tamil (FLEURS, real voices) | 5 | 38% | 51% | 31% |
| US English (FLEURS, real voices) | 5 | 3% | 3% | 5% |

## 2. Computer voices (a computer voice reads the sentence, the speech-to-text hears it back)

| Language | Clips | Clean | Phone 8 kHz | Phone mu-law |
|---|---|---|---|---|
| Hinglish | 5 | 1% | 4% | 3% |
| English | 5 | 1% | 3% | 4% |
| Hindi | 5 | 6% | 20% | 8% |
| Tamil | 5 | 13% | 25% | 10% |

## 3. Noisy clips (real voices only, shown separately)

| Voices | Clean | Phone 8 kHz | Phone mu-law | What the noise is |
|---|---|---|---|---|
| Hinglish (your recordings) | 93% | 100% | 100% | your recording with real background noise |
| Indian English (your recordings) | 8% | 8% | 8% | your recording with real background noise |
| Hindi (FLEURS, real voices) | 18% | 9% | 18% | FLEURS clip + synthetic chatter at 10 dB |
| Tamil (FLEURS, real voices) | 43% | 29% | 29% | FLEURS clip + synthetic chatter at 10 dB |
| US English (FLEURS, real voices) | 0% | 0% | 0% | FLEURS clip + synthetic chatter at 10 dB |

## 4. One score per language: 70% real voices + 30% computer voices (quiet clips)

| Language | Clean | Phone 8 kHz | Phone mu-law |
|---|---|---|---|
| Hinglish | 54% | 59% | 59% |
| Indian English | 7% | 6% | 8% |
| Hindi | 16% | 24% | 21% |
| Tamil | 30% | 43% | 25% |

## 5. Your own clips, one by one (WER, and WER of the sentence found inside what was heard)

The second number ignores extra words spoken before or after the sentence (for example 'Hello, haan ji...'). A big gap means you said more than the listed sentence, not that the speech-to-text was wrong.

| Clip | Noise | Clean | Phone 8 kHz | Phone mu-law | Heard (clean) |
|---|---|---|---|---|---|
| english-01 |  | 12% / 12% | 12% / 12% | 12% / 12% | My Zomato order came 40 minutes late, and the food would was cold, and I want a refund. |
| english-02 |  | 0% / 0% | 0% / 0% | 0% / 0% | my laptop charger stopped working and it is still under warranty. |
| english-03 |  | 20% / 20% | 7% / 7% | 20% / 20% | I paid 2,000 rupees through uh through PhonePe. But the money did not reached the other pe |
| english-04 |  | 8% / 8% | 8% / 8% | 8% / 8% | My indigo flight cancelled and they have not refunded my ticket yet. |
| english-05 | noisy | 8% / 0% | 8% / 0% | 8% / 0% | Hello. My Airtel Broadband is not working since yesterday. Please get it fixed. |
| hinglish-01 |  | 100% / 13% | 100% / 13% | 100% / 13% | Hello, haan ji, to mera complaint tha ki mera Swiggy ka order ek ghante late aaya aur khan |
| hinglish-02 |  | 100% / 29% | 100% / 21% | 100% / 21% | ho gaya, a toh pagal hi ho gaya tha tension ho gaya, kya tension hua tha? Main ne JIO ka 2 |
| hinglish-03 |  | 100% / 71% | 100% / 64% | 100% / 71% | Hello maine UPI se ah apne dost ko 1500 rupe bheje the jisme se paise kat gaye hain par ah |
| hinglish-04 |  | 8% / 8% | 31% / 23% | 31% / 23% | Mera order number 4839201 hai. Amazon me galat size ki kurti bhej di. |
| hinglish-05 | noisy | 93% / 71% | 100% / 86% | 100% / 79% | kiya, University ke ticket cancel kiye the aapke 10 din pehle. Jo uske regarding aaya hua  |

## 5b. Does phone quality change what is heard? (your clips: how different is the phone transcript from the clean one)

This needs no ground truth, so it is fair even for clips where you did not read the listed sentence word for word.

| Clip | Phone 8 kHz differs from clean by | Phone mu-law differs from clean by |
|---|---|---|
| english-01 | 0% | 0% |
| english-02 | 0% | 0% |
| english-03 | 12% | 18% |
| english-04 | 0% | 0% |
| english-05 | 0% | 0% |
| hinglish-01 | 12% | 2% |
| hinglish-02 | 31% | 22% |
| hinglish-03 | 11% | 11% |
| hinglish-04 | 23% | 23% |
| hinglish-05 | 88% | 82% |
| **average** | **18%** | **16%** |

## 6. Numbers heard exactly right?

| Clip | Source | Expected | Clean | Phone 8 kHz | Phone mu-law |
|---|---|---|---|---|---|
| english-01 | own | 40 | OK | OK | OK |
| english-03 | own | 2000 | OK | OK | OK |
| english-01 | synth | 40 | OK | OK | OK |
| english-03 | synth | 2000 | OK | OK | OK |
| hinglish-02 | own | 299 | OK | OK | OK |
| hinglish-03 | own | 1500 | OK | OK | OK |
| hinglish-04 | own | 4839201 | OK | OK | OK |
| hinglish-02 | synth | 299 | OK | OK | OK |
| hinglish-03 | synth | 1500 | OK | OK | OK |
| hinglish-04 | synth | 4839201 | OK | OK | OK |

**30 of 30 number checks passed.**

## Speed of one speech-to-text call (not streaming): median 10.1s, slowest 49.4s (144 calls)

## Worst 8 real-voice clips (what was said vs what was heard)

| Clip | Condition | WER | Reference | Heard |
|---|---|---|---|---|
| hindi-fleurs-03 | clean | 100% | इस सीज़न में बीमारी के शुरुआती मामले जुलाई के आखिर में सामने आए थे. | Is season mein bimari ke shuruati mamle July ke aakhir mein samne aaye the. |
| hindi-fleurs-03 | phone_8k | 100% | इस सीज़न में बीमारी के शुरुआती मामले जुलाई के आखिर में सामने आए थे. | Is season mein bimari ke shuruati mamle July ki aakhir mein samne aaye the. |
| hindi-fleurs-03 | phone_mulaw | 100% | इस सीज़न में बीमारी के शुरुआती मामले जुलाई के आखिर में सामने आए थे. | This Season mein bimari ke shuruati mamle July ke aakhir mein samne aaye the. |
| hinglish-05 | phone_8k | 100% | Mera IRCTC ticket cancel kiya tha das din pehle, refund abhi tak nahi  | mere 9 months ki bachchi thi jo ki aapse 10 din pehle |
| hinglish-05 | phone_mulaw | 100% | Mera IRCTC ticket cancel kiya tha das din pehle, refund abhi tak nahi  | ye aa gaya hai yeh delivery aa gaya hai 10 din pehle yeh jo correspondence aaya hai |
| tamil-fleurs-03 | phone_8k | 86% | வரைவு பகுப்பாய்வின் முடிவு ஒரு பொது வலைத்தளத்திற்கு வெளியிடப்படும். | வரைவுப் படிவங்களின் முடிவுகள் ஒரு ஒருபோதும் வலைத்தளத்திற்கு வழி இடப்படும். |
| hinglish-03 | clean | 100% | UPI se 1500 rupaye bheje, paise kat gaye par saamne wale ko nahi mile. | Hello maine UPI se ah apne dost ko 1500 rupe bheje the jisme se paise kat gaye hain par ah |
| hinglish-03 | phone_mulaw | 100% | UPI se 1500 rupaye bheje, paise kat gaye par saamne wale ko nahi mile. | hello maine UPI se a, apne dost ko 1500 rupe bhej diye the, jisme se paise kat gaye hain,  |
