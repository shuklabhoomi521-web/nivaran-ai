# Speech bake-off (Phase 3)

- Date: 2026-10-19; speech-to-text `sarvam:saaras:v3:hinglish=transcribe`; text-to-speech `gemini:gemini-3.8-flash-tts` (voice `Kore`)
- Language hint given to the speech-to-text: YES (the app knows the language the user picked)
- Numbers are WORD ERROR RATE (WER): lower is better, 0% is perfect. Phone 8 kHz = telephone sampling rate. mu-law = 8 kHz squeezed like a real phone line.
- 'Two thousand' and '2000', or 'forty' and '40', count as the same when scoring words; the number check below is strict.

## 1. Real voices, quiet clips (word error rate)

For your own clips the second number ignores extra words you spoke around the sentence (see table 5).

| Voices | Clips | Clean | Phone 8 kHz | Phone mu-law |
|---|---|---|---|---|
| Hinglish (your recordings) | 4 | 77% (sentence inside: 30%) | 81% (sentence inside: 34%) | 81% (sentence inside: 34%) |

## 2. Computer voices (a computer voice reads the sentence, the speech-to-text hears it back)

| Language | Clips | Clean | Phone 8 kHz | Phone mu-law |
|---|---|---|---|---|
| Hinglish | 5 | 14% | 14% | 14% |

## 3. Noisy clips (real voices only, shown separately)

| Voices | Clean | Phone 8 kHz | Phone mu-law | What the noise is |
|---|---|---|---|---|
| Hinglish (your recordings) | 71% | 79% | 79% | your recording with real background noise |

## 4. One score per language: 70% real voices + 30% computer voices (quiet clips)

| Language | Clean | Phone 8 kHz | Phone mu-law |
|---|---|---|---|
| Hinglish | 58% | 61% | 61% |
| Indian English | - | - | - |
| Hindi | - | - | - |
| Tamil | - | - | - |

## 5. Your own clips, one by one (WER, and WER of the sentence found inside what was heard)

The second number ignores extra words spoken before or after the sentence (for example 'Hello, haan ji...'). A big gap means you said more than the listed sentence, not that the speech-to-text was wrong.

| Clip | Noise | Clean | Phone 8 kHz | Phone mu-law | Heard (clean) |
|---|---|---|---|---|---|
| hinglish-01 |  | 100% / 20% | 100% / 20% | 100% / 20% | हेलो, हाँ जी, तो मेरा कंप्लेंट था कि मेरा स्विगी का ऑर्डर 1 घंटे लेट आया और खाना बिल्कुल ठ |
| hinglish-02 |  | 100% / 29% | 100% / 29% | 100% / 29% | क्या है? अब तो भाग आ गया, फोन किया था, टेंशन हो गया, क्या टेंशन हुआ था? मैंने जिओ का 299 व |
| hinglish-03 |  | 100% / 64% | 100% / 64% | 100% / 64% | हेलो, मैंने यूपीएल से अपने दोस्त को ₹1500 भेजे थे जिसमें से पैसे कट गए हैं पर मेरे दोस्त क |
| hinglish-04 |  | 8% / 8% | 23% / 23% | 23% / 23% | मेरा ऑर्डर नंबर 4839201 है, अमेज़ॉन ने गलत साइज़ की कुर्ती भेज दी। |
| hinglish-05 | noisy | 71% / 50% | 79% / 64% | 79% / 64% | मैंने आईआरएस शूटिंग से टिकट कैंसिल किया था 10 दिन पहले, तब तक मुझे उसका रिफंड नहीं आया। |

## 5b. Does phone quality change what is heard? (your clips: how different is the phone transcript from the clean one)

This needs no ground truth, so it is fair even for clips where you did not read the listed sentence word for word.

| Clip | Phone 8 kHz differs from clean by | Phone mu-law differs from clean by |
|---|---|---|
| hinglish-01 | 0% | 0% |
| hinglish-02 | 13% | 13% |
| hinglish-03 | 0% | 0% |
| hinglish-04 | 23% | 15% |
| hinglish-05 | 44% | 50% |
| **average** | **16%** | **16%** |

## 6. Numbers heard exactly right?

| Clip | Source | Expected | Clean | Phone 8 kHz | Phone mu-law |
|---|---|---|---|---|---|
| hinglish-02 | own | 299 | OK | OK | OK |
| hinglish-03 | own | 1500 | OK | OK | OK |
| hinglish-04 | own | 4839201 | OK | OK | OK |
| hinglish-02 | synth | 299 | OK | OK | OK |
| hinglish-03 | synth | 1500 | WRONG: heard no number | WRONG: heard no number | WRONG: heard no number |
| hinglish-04 | synth | 4839201 | OK | OK | OK |

**15 of 18 number checks passed.** Mistakes: hinglish-03 (synth, clean): heard []; hinglish-03 (synth, phone_8k): heard []; hinglish-03 (synth, phone_mulaw): heard []

## Speed of one speech-to-text call (not streaming): median 0.9s, slowest 1.3s (30 calls)

## Worst 8 real-voice clips (what was said vs what was heard)

| Clip | Condition | WER | Reference | Heard |
|---|---|---|---|---|
| hinglish-03 | clean | 100% | UPI se 1500 rupaye bheje, paise kat gaye par saamne wale ko nahi mile. | हेलो, मैंने यूपीएल से अपने दोस्त को ₹1500 भेजे थे जिसमें से पैसे कट गए हैं पर मेरे दोस्त क |
| hinglish-03 | phone_8k | 100% | UPI se 1500 rupaye bheje, paise kat gaye par saamne wale ko nahi mile. | हेलो, मैंने यूपीएल से अपने दोस्त को ₹1500 भेजे थे, जिसमें से पैसे कट गए हैं, पर मेरे दोस्त |
| hinglish-03 | phone_mulaw | 100% | UPI se 1500 rupaye bheje, paise kat gaye par saamne wale ko nahi mile. | हेलो, मैंने यूपीएल से अपने दोस्त को ₹1500 भेजे थे, जिसमें से पैसे कट गए हैं, पर मेरे दोस्त |
| hinglish-05 | phone_8k | 79% | Mera IRCTC ticket cancel kiya tha das din pehle, refund abhi tak nahi  | मैंने आईआरएस टीटी के पीछे ट्रैंक किया था दस दिन पहले, उसका जो है उसका रिफंड नहीं आया। |
| hinglish-05 | phone_mulaw | 79% | Mera IRCTC ticket cancel kiya tha das din pehle, refund abhi tak nahi  | मैंने आईआरएस टीटी के पीछे कैंपिड किया था दस दिन पहले। उसका जो है उसका रिफाइन नहीं आया। |
| hinglish-05 | clean | 71% | Mera IRCTC ticket cancel kiya tha das din pehle, refund abhi tak nahi  | मैंने आईआरएस शूटिंग से टिकट कैंसिल किया था 10 दिन पहले, तब तक मुझे उसका रिफंड नहीं आया। |
| hinglish-02 | clean | 100% | Maine Jio ka 299 wala recharge kiya tha but data abhi tak nahi aaya. | क्या है? अब तो भाग आ गया, फोन किया था, टेंशन हो गया, क्या टेंशन हुआ था? मैंने जिओ का 299 व |
| hinglish-02 | phone_8k | 100% | Maine Jio ka 299 wala recharge kiya tha but data abhi tak nahi aaya. | क्या है? तो बाहर से फोन किया था, टेंशन हो गया, क्या टेंशन हुआ था? मैंने जिओ का 299 वाला रि |
