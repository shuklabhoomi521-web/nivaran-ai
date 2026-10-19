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


_UNITS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
          "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
          "seventeen": 17, "eighteen": 18, "nineteen": 19}
_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
_SCALES = {"hundred": 100, "thousand": 1000, "lakh": 100000, "lakhs": 100000}
_NUM_WORDS = set(_UNITS) | set(_TENS) | set(_SCALES)


def _words_to_numbers(words: list[str]) -> list[str]:
    """'two thousand' -> '2000', 'forty' -> '40', 'fifteen hundred' -> '1500'.
    A run of plain digit words ('four eight three') is left alone: it is a number said digit by digit."""
    out, i = [], 0
    while i < len(words):
        if words[i] not in _NUM_WORDS:
            out.append(words[i])
            i += 1
            continue
        j = i
        while j < len(words) and (words[j] in _NUM_WORDS or (words[j] == "and" and j + 1 < len(words) and words[j + 1] in _NUM_WORDS and j > i)):
            j += 1
        run = [w for w in words[i:j] if w != "and"]
        if all(w in _UNITS and _UNITS[w] < 10 for w in run):       # digit by digit (or a single digit word)
            out.extend(run)
        else:
            total, current = 0, 0
            for w in run:
                if w in _UNITS:
                    current += _UNITS[w]
                elif w in _TENS:
                    current += _TENS[w]
                elif w == "hundred":
                    current = max(current, 1) * 100
                else:
                    total += max(current, 1) * _SCALES[w]
                    current = 0
            out.append(str(total + current))
        i = j
    return out


def normalize(text: str, digit_words: bool = True) -> str:
    """Lowercase, no punctuation, digits as digits, a run of single digits joined ('4 8 3' -> '483'),
    and stretched letters squeezed ('thandaa' -> 'thanda')."""
    t = unicodedata.normalize("NFC", text).casefold()
    t = re.sub(r"(?<=\d),(?=\d{3}\b)", "", t)          # 1,500 -> 1500
    t = "".join(_NATIVE_DIGITS.get(c, c) for c in t)
    # keep letters, combining vowel marks (Hindi and Tamil need them), numbers and spaces; everything else is punctuation
    t = "".join(c if (unicodedata.category(c)[0] in "LMN" or c.isspace()) else " " for c in t)
    words = t.split()
    if digit_words:
        words = _words_to_numbers(words)
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


def wer_inside(reference: str, hypothesis: str) -> float:
    """Word error rate of the reference sentence found INSIDE what was heard: extra words before or after the sentence
    are free (for example 'Hello, haan ji, ...' said before the sentence). Everything inside the sentence still counts."""
    ref, hyp = normalize(reference).split(), normalize(hypothesis).split()
    if not ref:
        return 0.0
    prev = [0] * (len(hyp) + 1)                 # start anywhere in the heard text for free
    for i, x in enumerate(ref, 1):
        cur = [i]
        for j, y in enumerate(hyp, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return min(1.0, min(prev) / len(ref))        # and end anywhere for free


def numbers_in(text: str) -> list[str]:
    """Every number in the text as digits, after turning 'two thousand' into 2000."""
    return re.findall(r"\d+", normalize(text))
