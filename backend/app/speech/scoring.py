"""Word and character error rates for speech-to-text tests (0.0 = perfect, 1.0 = every word wrong)."""
import re
import unicodedata

_EN_DIGITS = {"zero": "0", "oh": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6",
              "seven": "7", "eight": "8", "nine": "9"}
# English digit words as people write them in Hindi and Tamil script, plus the native digit words.
_HI_DIGITS = {"जीरो": "0", "ज़ीरो": "0", "शून्य": "0", "वन": "1", "एक": "1", "टू": "2", "दो": "2", "थ्री": "3", "तीन": "3",
              "फोर": "4", "चार": "4", "फाइव": "5", "पांच": "5", "पाँच": "5", "सिक्स": "6", "छह": "6", "छः": "6",
              "सेवन": "7", "सात": "7", "एट": "8", "ऐट": "8", "आठ": "8", "नाइन": "9", "नौ": "9"}
_TA_DIGITS = {"ஜீரோ": "0", "பூஜ்யம்": "0", "வன்": "1", "ஒன்று": "1", "டூ": "2", "இரண்டு": "2", "த்ரீ": "3", "மூன்று": "3",
              "ஃபோர்": "4", "நான்கு": "4", "ஃபைவ்": "5", "ஐந்து": "5", "சிக்ஸ்": "6", "ஆறு": "6", "செவன்": "7", "ஏழு": "7",
              "எய்ட்": "8", "எட்டு": "8", "நைன்": "9", "ஒன்பது": "9"}
_DIGIT_WORDS = {**_EN_DIGITS, **_HI_DIGITS, **_TA_DIGITS}
_NATIVE_DIGITS = {c: str(i) for i, c in enumerate("०१२३४५६७८९")}
_NATIVE_DIGITS.update({c: str(i) for i, c in enumerate("௦௧௨௩௪௫௬௭௮௯")})


def normalize(text: str, digit_words: bool = True) -> str:
    """Lowercase, no punctuation, digits as digits, a run of single digits joined ('4 8 3' -> '483'),
    and stretched letters squeezed ('thandaa' -> 'thanda')."""
    t = unicodedata.normalize("NFC", text).casefold()
    t = "".join(_NATIVE_DIGITS.get(c, c) for c in t)
    # keep letters, combining vowel marks (Hindi and Tamil need them), numbers and spaces; everything else is punctuation
    t = "".join(c if (unicodedata.category(c)[0] in "LMN" or c.isspace()) else " " for c in t)
    words = t.split()
    if digit_words:
        words = [_DIGIT_WORDS.get(w, w) for w in words]
    out, run = [], ""
    for w in words:
        if re.fullmatch(r"\d", w):
            run += w
            continue
        if run:
            out.append(run)
            run = ""
        out.append(w)
    if run:
        out.append(run)
    t = " ".join(out)
    t = re.sub(r"([a-z])\1+", r"\1", t)
    return t


def _edit_distance(a: list, b: list) -> int:
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def wer(reference: str, hypothesis: str) -> float:
    ref, hyp = normalize(reference).split(), normalize(hypothesis).split()
    if not ref:
        return 0.0 if not hyp else 1.0
    return min(1.0, _edit_distance(ref, hyp) / len(ref))


def cer(reference: str, hypothesis: str) -> float:
    ref, hyp = list(normalize(reference).replace(" ", "")), list(normalize(hypothesis).replace(" ", ""))
    if not ref:
        return 0.0 if not hyp else 1.0
    return min(1.0, _edit_distance(ref, hyp) / len(ref))


def digits_in(text: str) -> str:
    """All digits the speaker said, in order (after the same normalisation)."""
    return "".join(re.findall(r"\d", normalize(text)))
