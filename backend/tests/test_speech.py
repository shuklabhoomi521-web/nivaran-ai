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
    monkeypatch.setenv("STT_FALLBACK", "none")
    monkeypatch.setenv("TTS_FALLBACK", "none")
    with pytest.raises(ConfigError):
        make_stt()
    with pytest.raises(ConfigError):
        make_tts()


def test_prompt_based_provider_is_available(monkeypatch):
    monkeypatch.setenv("STT_PROVIDER", "gemini_prompt")
    assert get_settings().stt_provider == "gemini_prompt"
    assert get_settings().gemini_prompt_stt_model == "gemini-3.5-flash-lite"


def test_speech_defaults(monkeypatch):
    for k in ("STT_PROVIDER", "TTS_PROVIDER", "STT_FALLBACK", "TTS_FALLBACK", "GEMINI_STT_MODEL", "GEMINI_TTS_MODEL", "SPEECH_RPM"):
        monkeypatch.delenv(k, raising=False)
    s = get_settings()
    assert (s.stt_provider, s.tts_provider) == ("sarvam", "sarvam")           # Sarvam first
    assert (s.stt_fallback, s.tts_fallback) == ("gemini_prompt", "gemini")    # Gemini is the backup
    assert s.gemini_stt_model == "gemini-3.5-transcribe" and s.speech_rpm == 6
    assert s.gemini_tts_model == "gemini-3.8-flash-lite-tts"      # the dedicated flash-tts model hung during tests


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
        assert [s["id"] for s in sents] == [f"{lang}-0{i}" for i in range(1, 6)]
    assert any("4839201" in s["text"] for s in data["hinglish"]["sentences"])
    assert all("text_alt" in s for s in data["hinglish"]["sentences"])


def test_numbers_said_in_words_match_digits():
    from app.speech.scoring import numbers_in, wer, wer_inside
    assert numbers_in("I paid two thousand rupees") == ["2000"] == numbers_in("I paid 2000 rupees")
    assert numbers_in("forty minutes late") == ["40"]
    assert numbers_in("UPI se \u20b91,500 bheje") == ["1500"] == numbers_in("fifteen hundred rupaye")
    assert numbers_in("Jio ka 299 wala recharge") == ["299"]
    assert wer("I paid two thousand rupees", "I paid 2000 rupees") == 0


def test_extra_words_around_the_sentence_do_not_count_in_wer_inside():
    from app.speech.scoring import wer, wer_inside
    ref = "mera order number hai"
    heard = "hello haan ji mera order number hai thank you"
    assert wer(ref, heard) >= 1.0 and wer_inside(ref, heard) == 0
    assert wer_inside(ref, "hello mera order nambar hai") == pytest.approx(0.25)


class _FakeSarvamSTT:
    def __init__(self):
        self.kwargs = None

    def transcribe(self, **kw):
        self.kwargs = kw
        from types import SimpleNamespace
        return SimpleNamespace(transcript=" namaste duniya ", language_code="hi-IN")


class _FakeSarvamTTS:
    def convert(self, **kw):
        import base64
        from types import SimpleNamespace
        self.kwargs = kw
        return SimpleNamespace(audios=[base64.b64encode(b"AB").decode(), base64.b64encode(b"CD").decode()])


def _sarvam(stt=None, tts=None):
    from types import SimpleNamespace
    return SimpleNamespace(speech_to_text=stt or _FakeSarvamSTT(), text_to_speech=tts or _FakeSarvamTTS())


def test_sarvam_stt_maps_our_language_hints(tmp_path):
    from app.brain.ratelimit import RateLimiter
    from app.speech.sarvam import SarvamSTT
    fake = _FakeSarvamSTT()
    lim = RateLimiter(0, 0, usage_file=tmp_path / "u.json")
    stt = SarvamSTT(client=_sarvam(stt=fake), limiter=lim)
    assert stt.transcribe(b"wav", "audio/wav", "ta-IN").text == "namaste duniya"
    assert (fake.kwargs["language_code"], fake.kwargs["mode"]) == ("ta-IN", "transcribe")
    stt.transcribe(b"wav", "audio/wav", "hinglish")            # Hinglish default: Hindi words in Hindi script, English words as they are
    assert (fake.kwargs["language_code"], fake.kwargs["mode"]) == ("hi-IN", "codemix")
    import os
    os.environ["SARVAM_HINGLISH_MODE"] = "translit"
    try:
        SarvamSTT(client=_sarvam(stt=fake), limiter=lim).transcribe(b"wav", "audio/wav", "hinglish")
        assert fake.kwargs["mode"] == "translit"
    finally:
        del os.environ["SARVAM_HINGLISH_MODE"]
    stt.transcribe(b"wav", "audio/wav", None)                  # no hint: let Sarvam decide
    assert fake.kwargs["language_code"] == "unknown"
    assert fake.kwargs["file"][1] == b"wav" and fake.kwargs["input_audio_codec"] == "wav"


def test_sarvam_tts_joins_audio_and_can_make_phone_audio(tmp_path):
    from app.brain.ratelimit import RateLimiter
    from app.speech.sarvam import SarvamTTS
    fake = _FakeSarvamTTS()
    tts = SarvamTTS(client=_sarvam(tts=fake), limiter=RateLimiter(0, 0, usage_file=tmp_path / "u.json"))
    a = tts.synthesize("hello", "en-IN", codec="mulaw", sample_rate=8000)
    assert a.data == b"ABCD" and a.sample_rate == 8000 and a.mime_type == "audio/mulaw"
    assert fake.kwargs["output_audio_codec"] == "mulaw" and fake.kwargs["speech_sample_rate"] == 8000
    assert fake.kwargs["speaker"] == "simran_en_customer"


def test_sarvam_without_a_key_says_where_to_get_one(monkeypatch):
    monkeypatch.delenv("SARVAM_API_KEY", raising=False)
    monkeypatch.setenv("STT_PROVIDER", "sarvam")
    with pytest.raises(ConfigError, match="dashboard.sarvam.ai"):
        make_stt(fallback=False)


def test_sarvam_v4_gets_company_names_as_keyterms(tmp_path):
    from app.brain.ratelimit import RateLimiter
    from app.speech.sarvam import SarvamSTT, company_names
    fake = _FakeSarvamSTT()
    SarvamSTT(client=_sarvam(stt=fake), limiter=RateLimiter(0, 0, usage_file=tmp_path / "u.json")).transcribe(b"w", "audio/wav", "hinglish")
    assert "IRCTC" in fake.kwargs["keyterms"] and "Swiggy" in fake.kwargs["keyterms"]
    assert set(fake.kwargs["keyterms"]) == set(company_names()) and len(company_names()) == 40


# ---- credits and fallback ----
class _Boom:
    def __init__(self):
        self.calls = 0

    def transcribe(self, audio, mime_type, language=None):
        from app.speech.base import SpeechError
        self.calls += 1
        raise SpeechError("Sarvam stt error 500")


def _ledger(tmp_path, spent=0.0, start=100.0):
    from app.speech.credits import CreditLedger
    led = CreditLedger(file=tmp_path / "credits.json")
    led._start, led._seed = start, spent
    return led


def test_credit_ledger_counts_speech_and_text(tmp_path):
    import io
    import wave
    led = _ledger(tmp_path)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes(b"\x00\x00" * 16000 * 3600)       # one hour of audio
    led.add_stt(buf.getvalue())
    assert led.spent() == pytest.approx(30.0, rel=0.01)           # Rs 30 per hour
    led.add_tts(10000)
    assert led.spent() == pytest.approx(30.0 + 10000 * (2 / 1000 if led._tts_rate == 2 / 1000 else 3 / 1000), rel=0.01)


def test_credit_levels_and_warnings_only_get_worse(tmp_path):
    led = _ledger(tmp_path, spent=0)
    assert led.level() == "ok" and led.message() is None and led.warn_once() is None
    led = _ledger(tmp_path, spent=80)                       # Rs 20 left
    assert led.level() == "low" and "20" in led.message()
    assert led.warn_once() is not None and led.warn_once() is None     # only once per level
    (tmp_path / "b").mkdir(); (tmp_path / "c").mkdir()           # a fresh ledger file for each case
    assert _ledger(tmp_path / "b", spent=92).level() == "critical"
    assert _ledger(tmp_path / "c", spent=99).level() == "empty"


def test_fallback_uses_gemini_when_sarvam_fails():
    from app.speech.fallback import FallbackSTT
    boom, backup = _Boom(), FakeSTT("from the backup")
    f = FallbackSTT(lambda: boom, lambda: backup, "speech-to-text")
    t = f.transcribe(b"x", "audio/wav", "hi-IN")
    assert t.text == "from the backup" and t.provider == "backup" and f.fallbacks_used == 1 and boom.calls == 1


def test_fallback_skips_sarvam_when_credit_is_empty(tmp_path):
    from app.speech.fallback import FallbackSTT
    boom, backup = _Boom(), FakeSTT("backup")
    f = FallbackSTT(lambda: boom, lambda: backup, "speech-to-text", _ledger(tmp_path, spent=99))
    assert f.transcribe(b"x", "audio/wav").text == "backup"
    assert boom.calls == 0                                   # Sarvam was not even tried


def test_fallback_when_there_is_no_sarvam_key_runs_on_the_backup_only():
    from app.speech.fallback import FallbackSTT

    def no_key():
        raise ConfigError("SARVAM_API_KEY is not set")
    f = FallbackSTT(no_key, lambda: FakeSTT("backup only"), "speech-to-text")
    assert f.transcribe(b"x", "audio/wav").text == "backup only"


def test_fallback_keeps_the_primary_when_it_works():
    from app.speech.fallback import FallbackSTT
    f = FallbackSTT(lambda: FakeSTT("primary"), lambda: FakeSTT("backup"), "speech-to-text")
    t = f.transcribe(b"x", "audio/wav")
    assert t.text == "primary" and f.fallbacks_used == 0


def test_fallback_without_a_backup_raises_a_clear_error():
    from app.speech.base import SpeechError
    from app.speech.fallback import FallbackSTT
    f = FallbackSTT(lambda: _Boom(), None, "speech-to-text")
    with pytest.raises(SpeechError, match="no backup"):
        f.transcribe(b"x", "audio/wav")


def test_make_stt_builds_a_fallback_by_default(monkeypatch):
    from app.speech.fallback import FallbackSTT
    for k in ("STT_PROVIDER", "STT_FALLBACK"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.delenv("SARVAM_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    assert isinstance(make_stt(), FallbackSTT)


def test_voice_picks_choose_the_provider_per_language_and_the_other_one_is_the_backup(monkeypatch):
    from app.speech.base import SpeechAudio
    from app.speech.factory import RoutedTTS

    class P:
        def __init__(self, name, fail=False):
            self.name, self.fail = name, fail

        def synthesize(self, text, language=None, voice=None):
            if self.fail:
                raise RuntimeError("down")
            return SpeechAudio(data=b"x", mime_type="audio/wav", sample_rate=1, provider=self.name)

    r = RoutedTTS({"en-IN": "gemini", "hi-IN": "sarvam"}, "sarvam")
    r._cache = {"gemini": P("gemini"), "sarvam": P("sarvam")}
    assert r.synthesize("hi", "en-IN").provider == "gemini"
    assert r.synthesize("hi", "hi-IN").provider == "sarvam"
    assert r.synthesize("hi", "ta-IN").provider == "sarvam"          # no pick: the default
    r._cache["gemini"] = P("gemini", fail=True)
    assert r.synthesize("hi", "en-IN").provider == "sarvam" and r.fallbacks_used == 1


def test_auto_language_lets_sarvam_find_the_language_itself():
    from app.speech.sarvam import SarvamSTT

    seen = {}

    class R:
        transcript, language_code = "hello", "en-IN"

    class C:
        class speech_to_text:
            @staticmethod
            def transcribe(**kw):
                seen.update(kw)
                return R()

    from app.speech.credits import CreditLedger
    import tempfile, pathlib
    s = SarvamSTT(client=C(), ledger=CreditLedger(file=pathlib.Path(tempfile.mkdtemp()) / "l.json"))
    s.transcribe(b"RIFF" + b"\0" * 100, "audio/wav", "auto")
    assert seen["language_code"] == "unknown"


def test_a_voice_that_just_failed_is_skipped_for_a_while():
    from app.speech.base import SpeechAudio
    from app.speech.factory import RoutedTTS

    calls = []

    class P:
        def __init__(self, name, fail=False):
            self.name, self.fail = name, fail

        def synthesize(self, text, language=None, voice=None):
            calls.append(self.name)
            if self.fail:
                raise RuntimeError("down")
            return SpeechAudio(data=b"x", mime_type="audio/wav", sample_rate=1, provider=self.name)

    r = RoutedTTS({"en-IN": "gemini"}, "sarvam")
    r._cache = {"gemini": P("gemini", fail=True), "sarvam": P("sarvam")}
    r.synthesize("a", "en-IN"); r.synthesize("b", "en-IN")
    assert calls == ["gemini", "sarvam", "sarvam"]           # the second sentence did not wait for Gemini again


def test_groq_whisper_sends_the_language_and_returns_text(monkeypatch):
    import httpx
    from app.speech.groq import GroqSTT

    monkeypatch.setenv("GROQ_API_KEY", "test-key-not-real")
    seen = {}

    def post(url, data, files, headers, timeout):
        seen.update(url=url, data=data)
        return httpx.Response(200, json={"text": " namaste "})
    monkeypatch.setattr(httpx, "post", post)
    t = GroqSTT().transcribe(b"RIFF", "audio/wav", "hi-IN")
    assert t.text == "namaste" and t.provider == "groq" and seen["data"]["language"] == "hi"
    GroqSTT().transcribe(b"RIFF", "audio/wav", "auto")
    assert "language" not in seen["data"] and "prompt" in seen["data"]


def test_groq_whisper_errors_become_speech_errors(monkeypatch):
    import httpx
    from app.speech.base import SpeechError
    from app.speech.groq import GroqSTT

    monkeypatch.setenv("GROQ_API_KEY", "test-key-not-real")
    monkeypatch.setattr(httpx, "post", lambda *a, **k: httpx.Response(429, json={}))
    with pytest.raises(SpeechError):
        GroqSTT().transcribe(b"RIFF", "audio/wav", "en-IN")


def test_sarvam_is_paused_below_15_rupees_until_the_founder_says_yes(tmp_path, monkeypatch):
    import json

    from app.speech.credits import CreditLedger

    monkeypatch.delenv("SARVAM_ALLOW_LOW_CREDIT", raising=False)
    ledger = CreditLedger(file=tmp_path / "l.json")
    # started 100, spent 90 -> Rs 10 left
    (tmp_path / "l.json").write_text(json.dumps({"stt_seconds": 0.0, "tts_chars": 0, "seed_spent": 90.0, "warned": "ok"}))
    assert ledger.blocked() and "PAUSED" in ledger.message()
    monkeypatch.setenv("SARVAM_ALLOW_LOW_CREDIT", "yes")
    assert not ledger.blocked()                                   # the founder said yes
    (tmp_path / "l.json").write_text(json.dumps({"stt_seconds": 0.0, "tts_chars": 0, "seed_spent": 99.0, "warned": "ok"}))
    assert ledger.blocked()                                       # but below Rs 2 it stops anyway
    (tmp_path / "l.json").write_text(json.dumps({"stt_seconds": 0.0, "tts_chars": 0, "seed_spent": 50.0, "warned": "ok"}))
    monkeypatch.delenv("SARVAM_ALLOW_LOW_CREDIT")
    assert not ledger.blocked()                                   # Rs 50 left: fine


def test_local_model_turns_audio_into_text_without_loading_the_real_model(monkeypatch):
    import io
    import wave

    import numpy as np

    from app.speech import local

    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000)
        w.writeframes((np.zeros(8000)).astype("<i2").tobytes())
    seen = {}

    def fake_pipe(inputs):
        seen["rate"], seen["n"] = inputs["sampling_rate"], len(inputs["raw"])
        return {"text": " mera order late hai "}
    s = local.LocalWhisperSTT()
    monkeypatch.setattr(s, "_pipe", lambda: fake_pipe)
    t = s.transcribe(buf.getvalue(), "audio/wav", "hinglish")
    assert t.text == "mera order late hai" and t.provider == "local"
    assert seen["rate"] == 16000 and seen["n"] == 16000          # 8 kHz phone audio is resampled to 16 kHz
