# Record these now: Indian English and Hinglish (10 clips)

Real public clips already cover Hindi and Tamil (Google FLEURS) but not Indian-accented English or Hinglish, so those are the two to record.

| Folder (already exists) | File names to use |
|---|---|
| `~/nivaran/speech_test/recordings/english/` | `english-01.m4a`, `english-02.m4a`, `english-03.m4a`, `english-04.m4a`, `english-05.m4a` |
| `~/nivaran/speech_test/recordings/hinglish/` | `hinglish-01.m4a`, `hinglish-02.m4a`, `hinglish-03.m4a`, `hinglish-04.m4a`, `hinglish-05.m4a` |

- Speak in your natural Indian accent, at your normal speed.
- Clip **05** in each folder is the one **with background noise** (TV, fan, street). Clips 01-04 in a quiet room.
- Clip **03** has the order number: say the digits one by one in English.
- `.wav` or `.mp3` also work; keep the same file names.
- The exact words for every clip are in the tables below.

---

# Your recordings for the speech bake-off

You record **5 short clips in each of 4 languages (20 clips)**. These count 70% of the bake-off score, because real voices are messier than computer voices.

## How to record (Mac)

1. Open **QuickTime Player** → File → **New Audio Recording** (or the **Voice Memos** app).
2. Hold the Mac or phone about a hand-width from your mouth. Speak like you would on a call: natural speed, not slow and not reading-robot.
3. One sentence per recording. Stop the recording right after the sentence (1-2 seconds of silence at each end is fine).
4. Save each clip with the **exact file name** shown below (QuickTime saves `.m4a`; that is fine; `.wav` and `.mp3` also work).
5. Put the files in the folder for that language.

**Where to save:** `~/nivaran/speech_test/recordings/<language>/`

The folders already exist: `english`, `hindi`, `tamil`, `hinglish`. These files are never uploaded to GitHub (they are in `.gitignore`).

## The noisy clip

Clip **05** of every language must be recorded **with background noise**: play a TV, YouTube, a fan, or street noise at a normal volume while you speak. Keep the other 4 clips in a quiet room.

## Digits sentence (clip 03)

Clip 03 has an order number. Say the digits **one by one, in English** (four, eight, three, nine, two, zero, one), even inside a Hindi or Tamil sentence. That is how many people really say order numbers.

## The sentences to say

### English  →  save in `recordings/english/`

| File name | Say this |
|---|---|
| `english-01.m4a` | My Swiggy order came cold and I want a refund. |
| `english-02.m4a` | The flight was cancelled and nobody is giving me my money back. |
| `english-03.m4a` | My order number is four, eight, three, nine, two, zero, one. (digits one by one, in English) |
| `english-04.m4a` | I paid through PhonePe but the money was deducted and the payment failed. |
| `english-05.m4a` | Please tell the company that my internet has not worked for many days. **(with background noise)** |

### Hindi  →  save in `recordings/hindi/`

| File name | Say this |
|---|---|
| `hindi-01.m4a` | मेरा खाना ठंडा आया और मुझे पैसे वापस चाहिए। |
| `hindi-02.m4a` | मेरी ट्रेन की टिकट कैंसिल हुई लेकिन रिफंड नहीं आया। |
| `hindi-03.m4a` | मेरा ऑर्डर नंबर four eight three nine two zero one है। (अंक एक-एक करके, अंग्रेज़ी में) |
| `hindi-04.m4a` | यूपीआई से पैसे कट गए लेकिन भुगतान फेल हो गया। |
| `hindi-05.m4a` | कृपया कंपनी को बताइए कि मेरा इंटरनेट काम नहीं कर रहा। **(with background noise)** |

### Tamil  →  save in `recordings/tamil/`

| File name | Say this |
|---|---|
| `tamil-01.m4a` | என் ஆர்டர் குளிர்ந்து போய் வந்தது, எனக்கு பணம் திரும்ப வேண்டும். |
| `tamil-02.m4a` | என் இன்டர்நெட் மூன்று நாட்களாக வேலை செய்யவில்லை. |
| `tamil-03.m4a` | என் ஆர்டர் எண் four eight three nine two zero one. (எண்களை ஒவ்வொன்றாக, ஆங்கிலத்தில்) |
| `tamil-04.m4a` | ரயில் டிக்கெட்டை ரத்து செய்தேன், ஆனால் பணம் இன்னும் வரவில்லை. |
| `tamil-05.m4a` | தயவுசெய்து என் புகாரை நிறுவனத்திடம் சொல்லுங்கள். **(with background noise)** |

### Hinglish (Hindi in English letters, say it the way you speak)  →  save in `recordings/hinglish/`

| File name | Say this |
|---|---|
| `hinglish-01.m4a` | Mera khana thanda aaya, mujhe refund chahiye. |
| `hinglish-02.m4a` | Maine Amazon se kurti order ki thi, lekin alag aayi. |
| `hinglish-03.m4a` | Mera order number four eight three nine two zero one hai. (digits one by one, in English) |
| `hinglish-04.m4a` | UPI se paisa kat gaya lekin payment fail ho gaya. |
| `hinglish-05.m4a` | Please company ko bolo ki mera internet kaam nahi kar raha. **(with background noise)** |

## Check and run

After saving, tell me "recorded". I will run the bake-off and show you the scores before building anything else.

```bash
source .venv/bin/activate && python scripts/speech_bakeoff.py --only own
```

If you cannot record some clips, record what you can. Missing clips are skipped and marked in the report.
