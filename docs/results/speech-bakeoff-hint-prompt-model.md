# Speech bake-off (Phase 3)

- Language hint given to the speech-to-text: YES (the app knows the language the user picked)
- Date: 2026-10-19; STT `gemini_prompt:gemini-3.5-flash-lite`; TTS `gemini:gemini-3.8-flash-tts`, voice `Kore`
- WER = word error rate (lower is better; 0% perfect). Weighted score = 70% real human voices (your recordings + public FLEURS clips) + 30% synthetic round trip (if a language has no real voices yet, only the synthetic number is shown and marked).
- Conditions: clean = 16 kHz; phone 8 kHz = phone sampling rate; phone mu-law = 8 kHz squeezed like a real phone line.

## Real voices vs computer voices (word error rate, lower is better)

| Language | Condition | Real voices (own + public) | Computer voices (round trip) |
|---|---|---|---|
| english | clean | 2% | 2% |
| english | phone_8k | 3% | 2% |
| english | phone_mulaw | 4% | 2% |
| hindi | clean | 20% | 6% |
| hindi | phone_8k | 23% | 20% |
| hindi | phone_mulaw | 25% | 8% |
| tamil | clean | 39% | 13% |
| tamil | phone_8k | 48% | 25% |
| tamil | phone_mulaw | 30% | 10% |
| hinglish | clean | no real clips yet | 0% |
| hinglish | phone_8k | no real clips yet | 0% |
| hinglish | phone_mulaw | no real clips yet | 0% |

## Weighted word error rate by language and condition

| Language | Clean | Phone 8 kHz | Phone mu-law | Based on |
|---|---|---|---|---|
| english | 2% | 2% | 4% | real voices + synthetic |
| hindi | 16% | 22% | 20% | real voices + synthetic |
| tamil | 31% | 41% | 24% | real voices + synthetic |
| hinglish | 0% | 0% | 0% | synthetic only (NO real voices for this language yet) |

## Your own recordings only: WER / CER

| Language | Condition | WER | CER | Noisy clip WER |
|---|---|---|---|---|

## Public real-voice clips only (Google FLEURS: longer, formal read sentences; the noisy copy has synthetic chatter added): WER / CER

| Language | Condition | WER | CER | Noisy clip WER |
|---|---|---|---|---|
| english | clean | 2% | 3% | 0% |
| english | phone_8k | 3% | 3% | 0% |
| english | phone_mulaw | 4% | 3% | 0% |
| hindi | clean | 20% | 19% | 18% |
| hindi | phone_8k | 23% | 19% | 9% |
| hindi | phone_mulaw | 25% | 20% | 18% |
| tamil | clean | 39% | 11% | 43% |
| tamil | phone_8k | 48% | 13% | 29% |
| tamil | phone_mulaw | 30% | 10% | 29% |

## Synthetic round trip only: WER / CER

| Language | Condition | WER | CER | Noisy clip WER |
|---|---|---|---|---|
| english | clean | 2% | 0% | 0% |
| english | phone_8k | 2% | 0% | 0% |
| english | phone_mulaw | 2% | 0% | 0% |
| hindi | clean | 6% | 4% | 0% |
| hindi | phone_8k | 20% | 20% | 0% |
| hindi | phone_mulaw | 8% | 5% | 0% |
| tamil | clean | 13% | 3% | 40% |
| tamil | phone_8k | 25% | 21% | 0% |
| tamil | phone_mulaw | 10% | 3% | 40% |
| hinglish | clean | 0% | 0% | 0% |
| hinglish | phone_8k | 0% | 0% | 0% |
| hinglish | phone_mulaw | 0% | 0% | 0% |

## Speed of the speech-to-text call (non-streaming): median 10.1s, slowest 49.4s (114 calls)

## Order-number sentence: digits heard exactly?

| Language | Source | Condition | Digits right |
|---|---|---|---|
| english | synth | clean | yes |
| english | synth | phone_8k | yes |
| english | synth | phone_mulaw | yes |
| hindi | synth | clean | yes |
| hindi | synth | phone_8k | yes |
| hindi | synth | phone_mulaw | yes |
| tamil | synth | clean | yes |
| tamil | synth | phone_8k | yes |
| tamil | synth | phone_mulaw | yes |
| hinglish | synth | clean | yes |
| hinglish | synth | phone_8k | yes |
| hinglish | synth | phone_mulaw | yes |

## Worst 8 clips (what was said vs what was heard)

| Clip | Source | Condition | WER | Reference | Heard |
|---|---|---|---|---|---|
| hindi-fleurs-03 | public | clean | 100% | इस सीज़न में बीमारी के शुरुआती मामले जुलाई के आखिर में सामने आए थे. | Is season mein bimari ke shuruati mamle July ke aakhir mein samne aaye the. |
| hindi-fleurs-03 | public | phone_8k | 100% | इस सीज़न में बीमारी के शुरुआती मामले जुलाई के आखिर में सामने आए थे. | Is season mein bimari ke shuruati mamle July ki aakhir mein samne aaye the. |
| hindi-fleurs-03 | public | phone_mulaw | 100% | इस सीज़न में बीमारी के शुरुआती मामले जुलाई के आखिर में सामने आए थे. | This Season mein bimari ke shuruati mamle July ke aakhir mein samne aaye the. |
| tamil-01 | synth | phone_8k | 100% | என் ஆர்டர் குளிர்ந்து போய் வந்தது, எனக்கு பணம் திரும்ப வேண்டும். | En nadar kulirnthu poy vandhadhu, enakku panam thirumba vendum. |
| tamil-fleurs-03 | public | phone_8k | 86% | வரைவு பகுப்பாய்வின் முடிவு ஒரு பொது வலைத்தளத்திற்கு வெளியிடப்படும். | வரைவுப் படிவங்களின் முடிவுகள் ஒரு ஒருபோதும் வலைத்தளத்திற்கு வழி இடப்படும். |
| hindi-03 | synth | phone_8k | 80% | मेरा ऑर्डर नंबर 4839201 है। | mera order number 4839201 hai |
| tamil-fleurs-03 | public | clean | 71% | வரைவு பகுப்பாய்வின் முடிவு ஒரு பொது வலைத்தளத்திற்கு வெளியிடப்படும். | பழையவற்றுள் பாழாய்விடும் முடிவு, அது ஒரு பொது வலைத்தளத்திற்கு வழி இடப்படும். |
| tamil-fleurs-05 | public | phone_8k | 57% | மோல்டோவாவில் உள்ள முக்கிய மதம் ஆர்தடாக்ஸ் கிறிஸ்துவ மதம். | மேல் தோவாவில் உள்ள முக்கிய மதம் ஆர்த்தோடாக்ஸ் கிறித்தவ மதம். |
