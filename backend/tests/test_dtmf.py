import numpy as np

from app.voice.dtmf import tones


def test_each_digit_has_the_two_right_frequencies():
    for digit, (lo, hi) in {"1": (697, 1209), "5": (770, 1336), "9": (852, 1477), "0": (941, 1336)}.items():
        x = np.frombuffer(tones(digit, tone_ms=200, gap_ms=0), "<i2").astype(float)
        spec = np.abs(np.fft.rfft(x)); freqs = np.fft.rfftfreq(len(x), 1 / 8000)
        top2 = sorted(freqs[np.argsort(spec)[-2:]])
        assert abs(top2[0] - lo) < 8 and abs(top2[1] - hi) < 8, (digit, top2)


def test_length_and_unknown_characters():
    assert len(tones("12", tone_ms=100, gap_ms=50)) == 2 * (800 + 400) * 2
    assert tones("abc") == b""
