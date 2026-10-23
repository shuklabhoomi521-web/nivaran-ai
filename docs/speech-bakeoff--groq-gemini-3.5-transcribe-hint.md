# Speech bake-off (Phase 3)

- Date: 2026-10-23; speech-to-text `groq:gemini-3.5-transcribe`; text-to-speech `gemini:gemini-3.8-flash-lite-tts` (voice `Kore`)
- Language hint given to the speech-to-text: YES (the app knows the language the user picked)
- Numbers are WORD ERROR RATE (WER): lower is better, 0% is perfect. Phone 8 kHz = telephone sampling rate. mu-law = 8 kHz squeezed like a real phone line.
- 'Two thousand' and '2000', or 'forty' and '40', count as the same when scoring words; the number check below is strict.

## 1. Real voices, quiet clips (word error rate)

For your own clips the second number ignores extra words you spoke around the sentence (see table 5).

| Voices | Clips | Clean | Phone 8 kHz | Phone mu-law |
|---|---|---|---|---|
| Hinglish (your recordings) | 4 | 85% (sentence inside: 61%) | 87% (sentence inside: 64%) | 88% (sentence inside: 48%) |
| Indian English (your recordings) | 4 | 7% (sentence inside: 7%) | 7% (sentence inside: 7%) | 8% (sentence inside: 8%) |
| Hindi (FLEURS, real voices) | 5 | 20% | 19% | 19% |
| Tamil (FLEURS, real voices) | 5 | 43% | 45% | 44% |
| US English (FLEURS, real voices) | 5 | 4% | 4% | 4% |

## 2. Computer voices (a computer voice reads the sentence, the speech-to-text hears it back)

| Language | Clips | Clean | Phone 8 kHz | Phone mu-law |
|---|---|---|---|---|

## 3. Noisy clips (real voices only, shown separately)

| Voices | Clean | Phone 8 kHz | Phone mu-law | What the noise is |
|---|---|---|---|---|
| Hinglish (your recordings) | 86% | 93% | 86% | your recording with real background noise |
| Indian English (your recordings) | 17% | 17% | 17% | your recording with real background noise |
| Hindi (FLEURS, real voices) | 36% | 27% | 46% | FLEURS clip + synthetic chatter at 10 dB |
| Tamil (FLEURS, real voices) | 57% | 71% | 86% | FLEURS clip + synthetic chatter at 10 dB |
| US English (FLEURS, real voices) | 0% | 0% | 0% | FLEURS clip + synthetic chatter at 10 dB |

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
| english-01 |  | 6% / 6% | 6% / 6% | 6% / 6% | My Zomato order came 40 minutes late and the food was cold and I want a refund. |
| english-02 |  | 0% / 0% | 0% / 0% | 0% / 0% | My laptop charger stopped working and it is still under warranty. |
| english-03 |  | 13% / 13% | 13% / 13% | 20% / 20% | I paid 2000 rupees through phonepay but the money did not reach to the other person. |
| english-04 |  | 8% / 8% | 8% / 8% | 8% / 8% | My indigo flight cancelled and they have not refunded my ticket yet. |
| english-05 | noisy | 17% / 8% | 17% / 8% | 17% / 8% | Hello, my Airtel bootbank is not working since yesterday. Please get it fixed. |
| hinglish-01 |  | 100% / 33% | 100% / 40% | 100% / 40% | Hello! हाँ जी, तो मेरा कम्प्लेन था कि मेरा स्विगी का ओडर एक घंटे लेट आया और खाना बिल्कुल ठ |
| hinglish-02 |  | 100% / 79% | 100% / 100% | 100% / 29% | Hello! Hello! I had recharged Jio's 299 but the data has not come yet. Check it. Check it. |
| hinglish-03 |  | 100% / 93% | 100% / 71% | 100% / 71% | Hello! I sent my friend Rs.1500 from UTI. I have to deduct money from it. But my friend di |
| hinglish-04 |  | 38% / 38% | 46% / 46% | 54% / 54% | mera order number 4839301 hai, Amazon me delat size ki kurti bejde. |
| hinglish-05 | noisy | 86% / 86% | 93% / 86% | 86% / 86% | mera order Swiggy se aaya, mera order Swiggy se aaya, |

## 5b. Does phone quality change what is heard? (your clips: how different is the phone transcript from the clean one)

This needs no ground truth, so it is fair even for clips where you did not read the listed sentence word for word.

| Clip | Phone 8 kHz differs from clean by | Phone mu-law differs from clean by |
|---|---|---|
| english-01 | 0% | 0% |
| english-02 | 0% | 0% |
| english-03 | 0% | 12% |
| english-04 | 0% | 0% |
| english-05 | 8% | 8% |
| hinglish-01 | 5% | 5% |
| hinglish-02 | 100% | 100% |
| hinglish-03 | 96% | 96% |
| hinglish-04 | 42% | 50% |
| hinglish-05 | 100% | 100% |
| **average** | **35%** | **37%** |

## 6. Numbers heard exactly right?

| Clip | Source | Expected | Clean | Phone 8 kHz | Phone mu-law |
|---|---|---|---|---|---|
| english-01 | own | 40 | OK | OK | OK |
| english-03 | own | 2000 | OK | OK | OK |
| hinglish-02 | own | 299 | OK | WRONG: heard no number | OK |
| hinglish-03 | own | 1500 | OK | WRONG: heard 15000 | WRONG: heard 15 |
| hinglish-04 | own | 4839201 | WRONG: heard 4839301 | WRONG: heard 439201 | WRONG: heard 439, 01 |

**9 of 15 number checks passed.** Mistakes: hinglish-02 (own, phone_8k): heard []; hinglish-03 (own, phone_8k): heard ['15000']; hinglish-03 (own, phone_mulaw): heard ['15']; hinglish-04 (own, clean): heard ['4839301']; hinglish-04 (own, phone_8k): heard ['439201']; hinglish-04 (own, phone_mulaw): heard ['439', '01']

## Speed of one speech-to-text call (not streaming): median 0.9s, slowest 49.0s (84 calls)

## Worst 8 real-voice clips (what was said vs what was heard)

| Clip | Condition | WER | Reference | Heard |
|---|---|---|---|---|
| hinglish-02 | phone_8k | 100% | Maine Jio ka 299 wala recharge kiya tha but data abhi tak nahi aaya. | अगर आप बात करें तो आपको बात करें। |
| hinglish-03 | clean | 100% | UPI se 1500 rupaye bheje, paise kat gaye par saamne wale ko nahi mile. | Hello! I sent my friend Rs.1500 from UTI. I have to deduct money from it. But my friend di |
| tamil-fleurs-noisy-05 | phone_mulaw | 86% | மோல்டோவாவில் உள்ள முக்கிய மதம் ஆர்தடாக்ஸ் கிறிஸ்துவ மதம். | மெல்துவாவி உள்ள முக்கியமதம் ஆர்த்தோட்டாக்ஸ் திருத்துமதம் |
| hinglish-05 | clean | 86% | Mera IRCTC ticket cancel kiya tha das din pehle, refund abhi tak nahi  | mera order Swiggy se aaya, mera order Swiggy se aaya, |
| hinglish-05 | phone_8k | 93% | Mera IRCTC ticket cancel kiya tha das din pehle, refund abhi tak nahi  | ने आया रेस्टीटी की प्रांचन की आखा दस दुन पहले, तब मुझे उसका रिफाइन ने आया। |
| hinglish-05 | phone_mulaw | 86% | Mera IRCTC ticket cancel kiya tha das din pehle, refund abhi tak nahi  | या आरियारेश्टीरी की प्रांटन की आखा 10 दुन पहले तब मुझे उसका रिपाइन नहीं आया। |
| hinglish-02 | clean | 100% | Maine Jio ka 299 wala recharge kiya tha but data abhi tak nahi aaya. | Hello! Hello! I had recharged Jio's 299 but the data has not come yet. Check it. Check it. |
| hinglish-03 | phone_8k | 100% | UPI se 1500 rupaye bheje, paise kat gaye par saamne wale ko nahi mile. | Hello, मैंने UPI से अपने दोष्ट को 15,000 रुका भी देखे। जिसमें से पैसे कड़ना हैं पर मेरे दो |
