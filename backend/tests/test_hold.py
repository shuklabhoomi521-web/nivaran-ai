import numpy as np

from app.voice.hold import HoldDetector


def music(secs, rate=8000):
    t = np.arange(int(secs * rate)) / rate
    return (6000 * (np.sin(2 * np.pi * 440 * t) + np.sin(2 * np.pi * 554 * t) + np.sin(2 * np.pi * 659 * t)) / 3).astype("<i2").tobytes()


def feed(d, pcm, rate=8000):
    changed, step = [], rate // 50 * 2                       # 20 ms pieces
    for i in range(0, len(pcm), step):
        if d.audio(pcm[i:i + step], rate):
            changed.append(True)
    return changed


def test_ten_seconds_of_music_with_no_speech_means_on_hold():
    d = HoldDetector()
    assert not d.on_hold
    assert feed(d, music(12)) and d.on_hold


def test_not_on_hold_after_a_short_pause_in_a_normal_chat():
    d = HoldDetector()
    feed(d, music(4))
    assert not d.on_hold


def test_a_quiet_line_is_silence_not_hold():
    d = HoldDetector()
    feed(d, np.zeros(8000 * 20, "<i2").tobytes())
    assert not d.on_hold


def test_normal_conversation_is_never_hold():
    d = HoldDetector()
    for _ in range(6):                      # the agent talks (voice detector says speech) for 3 s, then 1 s of quiet
        d.speech(True); feed(d, music(3)); d.speech(False); feed(d, np.zeros(8000, "<i2").tobytes())
    assert not d.on_hold


def test_speech_after_the_music_ends_the_hold():
    d = HoldDetector()
    feed(d, music(12))
    assert d.on_hold
    d.speech(True)
    assert not d.on_hold
