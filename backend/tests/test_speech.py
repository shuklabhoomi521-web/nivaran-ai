import shutil
import sys
import wave
from pathlib import Path

import pytest

from app.config import ConfigError, get_settings
from app.speech.audio import CONDITIONS, render
from app.speech.factory import make_stt, make_tts
from app.speech.fakes import FakeSTT, FakeTTS
from app.speech.scoring import cer, digits_in, normalize, wer


def test_word_error_rate_basics():
    assert wer("my food came cold", "my food came cold") == 0
    assert wer("my food came cold", "my food came") == pytest.approx(0.25)
    assert wer("a b c d", "x y z w") == 1.0
    assert wer("hello", "") == 1.0


def test_punctuation_case_and_spelling_stretch_are_ignored():
    assert wer("Mera khana thanda aaya, mujhe refund chahiye.", "mera khana thandaa aya mujhe refund chahiye") < 0.35
    assert normalize("Mera khana thandaa") == "mera khana thanda"


def test_spoken_digits_become_one_number():
    assert normalize("My order number is four eight three nine two zero one") == "my order number is 4839201"
    assert normalize("order number 4 8 3 9 2 0 1") == "order number 4839201"
    assert digits_in("मेरा ऑर्डर नंबर फोर एट थ्री नाइन टू जीरो वन है") == "4839201"
    assert digits_in("என் ஆர்டர் எண் ஃபோர் எய்ட் த்ரீ நைன் டூ ஜீரோ வன்") == "4839201"
    assert wer("मेरा ऑर्डर नंबर 4839201 है", "मेरा ऑर्डर नंबर 4839201 है।") == 0


def test_wrong_digit_is_caught():
    assert digits_in("order 4839201") != digits_in("order 4839202")


def test_devanagari_and_tamil_scoring_work():
    assert wer("मेरा खाना ठंडा आया", "मेरा खाना ठंडा आया") == 0
    assert wer("என் இன்டர்நெட் வேலை செய்யவில்லை", "என் இன்டர்நெட் வேலை செய்கிறது") == pytest.approx(0.25)
    assert cer("ठंडा", "ठंडा") == 0


def test_fakes_follow_the_interfaces():
    stt, tts = FakeSTT("namaste"), FakeTTS()
    assert stt.transcribe(b"1234", "audio/wav", "hi-IN").text == "namaste"
    assert tts.synthesize("hello", "en-IN").mime_type == "audio/wav"
    assert stt.calls and tts.calls


def test_unknown_speech_provider_is_rejected(monkeypatch):
    monkeypatch.setenv("STT_PROVIDER", "banana")
    monkeypatch.setenv("TTS_PROVIDER", "banana")
    with pytest.raises(ConfigError):
        make_stt()
    with pytest.raises(ConfigError):
        make_tts()


def test_speech_defaults(monkeypatch):
    for k in ("STT_PROVIDER", "TTS_PROVIDER", "GEMINI_STT_MODEL", "GEMINI_TTS_MODEL", "SPEECH_RPM"):
        monkeypatch.delenv(k, raising=False)
    s = get_settings()
    assert (s.stt_provider, s.tts_provider) == ("gemini", "gemini")
    assert s.gemini_stt_model == "gemini-3.5-transcribe" and s.speech_rpm == 6


@pytest.mark.skipif(sys.platform != "darwin" or not shutil.which("afconvert"), reason="needs macOS afconvert")
@pytest.mark.parametrize("cond,rate", [("clean", 16000), ("phone_8k", 8000), ("phone_mulaw", 8000)])
def test_render_makes_mono_wav_at_the_right_rate(tmp_path, cond, rate):
    src = tmp_path / "in.wav"
    with wave.open(str(src), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000)
        w.writeframes(b"\x00\x10" * 24000)
    out = tmp_path / "out.wav"
    out.write_bytes(render(src, cond))
    with wave.open(str(out), "rb") as w:
        assert (w.getframerate(), w.getnchannels(), w.getsampwidth()) == (rate, 1, 2)
    assert set(CONDITIONS) == {"clean", "phone_8k", "phone_mulaw"}


def test_sentence_set_is_complete():
    import json
    root = Path(__file__).resolve().parents[2] / "speech_test" / "sentences.json"
    data = json.loads(root.read_text(encoding="utf-8"))
    assert set(data) == {"english", "hindi", "tamil", "hinglish"}
    for lang, block in data.items():
        sents = block["sentences"]
        assert len(sents) == 5
        assert sum(bool(s.get("noisy")) for s in sents) == 1, "exactly one noisy clip per language"
        assert any("4839201" in s["text"] for s in sents), "each language has the order-number sentence"
        assert [s["id"] for s in sents] == [f"{lang}-0{i}" for i in range(1, 6)]
    assert all("text_alt" in s for s in data["hinglish"]["sentences"])
