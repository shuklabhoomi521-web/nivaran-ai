# Speech bake-off (Phase 3)

- Date: 2026-10-17; STT `gemini_prompt:gemini-3.5-flash-lite`; TTS `gemini:gemini-3.8-flash-tts`, voice `Kore`
- WER = word error rate (lower is better; 0% perfect). Weighted score = 70% real human voices (your recordings + public FLEURS clips) + 30% synthetic round trip (if a language has no real voices yet, only the synthetic number is shown and marked).
- Conditions: clean = 16 kHz; phone 8 kHz = phone sampling rate; phone mu-law = 8 kHz squeezed like a real phone line.

## Real voices vs computer voices (word error rate, lower is better)

| Language | Condition | Real voices (own + public) | Computer voices (round trip) |
|---|---|---|---|
| english | clean | 1% | 2% |
| english | phone_8k | 3% | 0% |
| english | phone_mulaw | 5% | 2% |
| hindi | clean | 19% | 26% |
| hindi | phone_8k | 42% | 24% |
| hindi | phone_mulaw | 40% | 6% |
| tamil | clean | 53% | 37% |
| tamil | phone_8k | 51% | 48% |
| tamil | phone_mulaw | 58% | 43% |
| hinglish | clean | no real clips yet | 0% |
| hinglish | phone_8k | no real clips yet | 2% |
| hinglish | phone_mulaw | no real clips yet | 4% |

## Weighted word error rate by language and condition

| Language | Clean | Phone 8 kHz | Phone mu-law | Based on |
|---|---|---|---|---|
| english | 1% | 2% | 4% | real voices + synthetic |
| hindi | 21% | 36% | 30% | real voices + synthetic |
| tamil | 48% | 50% | 53% | real voices + synthetic |
| hinglish | 0% | 2% | 4% | synthetic only (NO real voices for this language yet) |

## Your own recordings only: WER / CER

| Language | Condition | WER | CER | Noisy clip WER |
|---|---|---|---|---|

## Public real-voice clips only (Google FLEURS: longer, formal read sentences; the noisy copy has synthetic chatter added): WER / CER

| Language | Condition | WER | CER | Noisy clip WER |
|---|---|---|---|---|
| english | clean | 1% | 1% | 0% |
| english | phone_8k | 3% | 3% | 0% |
| english | phone_mulaw | 5% | 3% | 0% |
| hindi | clean | 19% | 18% | 9% |
| hindi | phone_8k | 42% | 38% | 27% |
| hindi | phone_mulaw | 40% | 36% | 27% |
| tamil | clean | 53% | 22% | 100% |
| tamil | phone_8k | 51% | 28% | 29% |
| tamil | phone_mulaw | 58% | 41% | 100% |

## Synthetic round trip only: WER / CER

| Language | Condition | WER | CER | Noisy clip WER |
|---|---|---|---|---|
| english | clean | 2% | 0% | 0% |
| english | phone_8k | 0% | 0% | 0% |
| english | phone_mulaw | 2% | 0% | 0% |
| hindi | clean | 26% | 24% | 0% |
| hindi | phone_8k | 24% | 21% | 0% |
| hindi | phone_mulaw | 6% | 4% | 0% |
| tamil | clean | 37% | 40% | 0% |
| tamil | phone_8k | 48% | 42% | 40% |
| tamil | phone_mulaw | 43% | 35% | 40% |
| hinglish | clean | 0% | 0% | 0% |
| hinglish | phone_8k | 2% | 3% | 0% |
| hinglish | phone_mulaw | 4% | 1% | 0% |

## Speed of the speech-to-text call (non-streaming): median 10.1s, slowest 43.8s (114 calls)

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
| hindi-fleurs-03 | public | phone_8k | 100% | इस सीज़न में बीमारी के शुरुआती मामले जुलाई के आखिर में सामने आए थे. | Is season mein bimari ke shuruati mamle July ke aakhir mein samne aaye the. |
| hindi-fleurs-03 | public | phone_mulaw | 100% | इस सीज़न में बीमारी के शुरुआती मामले जुलाई के आखिर में सामने आए थे. | Is season mein bimari ke shuruati mamle July ke aakhir mein samne aaye the. |
| hindi-fleurs-04 | public | phone_8k | 100% | इसकी सर्वव्यापी शक्ति ने राजा से लेकर आम तक सभी को प्रभावित किया. | Iski sarvavyapi shakti ne raja se lekar aam tak sabhi ko prabhavit kiya. |
| hindi-fleurs-04 | public | phone_mulaw | 100% | इसकी सर्वव्यापी शक्ति ने राजा से लेकर आम तक सभी को प्रभावित किया. | Isaki sarvavyapi shakti ne raja se lekar aam tak sabhi ko prabhavit kiya. |
| tamil-fleurs-01 | public | phone_8k | 100% | அர்ஜெண்டினா உலகின் மிகச் சிறந்த போலோ குழுக்கள் மற்றும் விளையாட்டு வீரர்கள் கொண்டதற்கு பெயர் போனது. | Arjentina Ulaikkin mikacharan polo kulukal matrum vilayattu veerarkal kondadarku peyar ponathu. |
| tamil-fleurs-01 | public | phone_mulaw | 100% | அர்ஜெண்டினா உலகின் மிகச் சிறந்த போலோ குழுக்கள் மற்றும் விளையாட்டு வீரர்கள் கொண்டதற்கு பெயர் போனது. | Argentina_ulagin_migachirantha_polo_kuzhukkal_matrum_vilayattu_veerargal_kondadharku_peyar_ponathu. |
| tamil-fleurs-03 | public | clean | 100% | வரைவு பகுப்பாய்வின் முடிவு ஒரு பொது வலைத்தளத்திற்கு வெளியிடப்படும். | வளைவு பா(ஹு)ப் பாய்வின் முடிவு ஒரு பொது வலைத்தளத்திற்கு வழி இடப்படும். |
