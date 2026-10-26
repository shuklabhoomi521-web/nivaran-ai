import audioop

import numpy as np

from app.voice.phone_quality import LineDegrader


def tone(freq, rate=16000, secs=0.5):
    t = np.arange(int(rate * secs)) / rate
    return (9000 * np.sin(2 * np.pi * freq * t)).astype("<i2").tobytes()


def rms(pcm):
    return audioop.rms(pcm, 2)


def test_speech_band_survives_but_high_frequencies_are_cut_like_on_a_phone():
    d = LineDegrader()
    low, high = d.process(tone(1000), 16000), LineDegrader().process(tone(6000), 16000)
    assert rms(low) > 4000                      # a 1 kHz tone passes
    assert rms(high) < 1500                     # a 6 kHz hiss is gone (phones carry nothing above 4 kHz)


def test_output_has_the_same_length_and_rate_as_the_input():
    for rate in (16000, 24000, 48000):
        out = LineDegrader().process(tone(500, rate), rate)
        assert abs(len(out) - len(tone(500, rate))) < 200


def test_chunked_audio_gives_nearly_the_same_result_as_one_piece():
    whole = tone(800, secs=1.0)
    d = LineDegrader()
    pieces = b"".join(d.process(whole[i:i + 640], 16000) for i in range(0, len(whole), 640))
    assert abs(rms(pieces) - rms(LineDegrader().process(whole, 16000))) < 600


def test_empty_audio_is_fine():
    assert LineDegrader().process(b"", 16000) == b""
