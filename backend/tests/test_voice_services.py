import asyncio
import io
import wave

from pipecat.frames.frames import ErrorFrame, TranscriptionFrame, TTSAudioRawFrame, TTSStoppedFrame

from app.speech.base import SpeechAudio, SpeechError, Transcript
from app.speech.fakes import FakeSTT, FakeTTS
from app.voice.services import NivaranSTTService, NivaranTTSService


def _wav(seconds=0.2, rate=24000) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes(b"\x01\x00" * int(rate * seconds))
    return buf.getvalue()


async def _collect(gen):
    return [f async for f in gen]


class WavTTS(FakeTTS):
    def synthesize(self, text, language=None, voice=None):
        super().synthesize(text, language, voice)
        return SpeechAudio(data=_wav(), mime_type="audio/wav", sample_rate=24000, provider="fake")


def test_stt_service_returns_a_transcription_frame_and_passes_the_language_hint():
    fake = FakeSTT("mera order thanda hai")
    svc = NivaranSTTService(fake, language_hint="hinglish")
    frames = asyncio.run(_collect(svc.run_stt(_wav())))
    assert [type(f) for f in frames] == [TranscriptionFrame]
    assert frames[0].text == "mera order thanda hai"
    assert fake.calls[0][2] == "hinglish"          # the language the user picked reaches the provider


def test_stt_service_says_nothing_for_silence():
    assert asyncio.run(_collect(NivaranSTTService(FakeSTT("   ")).run_stt(_wav()))) == []


def test_stt_service_reports_a_provider_failure_instead_of_crashing():
    class Broken:
        def transcribe(self, *a, **k):
            raise SpeechError("both providers down")
    frames = asyncio.run(_collect(NivaranSTTService(Broken()).run_stt(_wav())))
    assert len(frames) == 1 and isinstance(frames[0], ErrorFrame) and "both providers down" in frames[0].error


def test_tts_service_turns_text_into_audio_frames():
    tts = WavTTS()
    svc = NivaranTTSService(tts, locale="ta-IN")
    frames = asyncio.run(_collect(svc.run_tts("வணக்கம்", "ctx1")))
    assert [type(f) for f in frames] == [TTSAudioRawFrame, TTSStoppedFrame]       # the audio, then "finished speaking"
    assert frames[0].sample_rate == 24000 and frames[0].num_channels == 1 and len(frames[0].audio) > 0
    assert tts.calls[0][:2] == ("வணக்கம்", "ta-IN")


def test_tts_service_reports_a_provider_failure():
    class Broken:
        def synthesize(self, *a, **k):
            raise SpeechError("voice down")
    frames = asyncio.run(_collect(NivaranTTSService(Broken()).run_tts("hi", "c")))
    assert len(frames) == 1 and isinstance(frames[0], ErrorFrame)
