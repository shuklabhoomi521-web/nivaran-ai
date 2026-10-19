"""The whole voice chain, with a real recorded clip and fake speech providers (no network, no microphone):
voice detector -> speech-to-text -> echo reply -> text-to-speech."""
import asyncio
import wave
from pathlib import Path

import pytest
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import InputAudioRawFrame, TranscriptionFrame, TTSAudioRawFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.processors.audio.vad_processor import VADProcessor
from pipecat.tests.utils import run_test

from app.speech.fakes import FakeSTT
from app.voice.services import NivaranSTTService, NivaranTTSService
from app.voice.spike_echo_bot import Echo
from tests.test_voice_services import WavTTS

CLIP = Path(__file__).resolve().parents[2] / "speech_test" / "recordings" / "english" / "english-02.wav"


def _frames(path: Path):
    with wave.open(str(path), "rb") as w:
        assert w.getframerate() == 16000 and w.getnchannels() == 1
        pcm = w.readframes(w.getnframes())
    chunk = 640   # 20 ms at 16 kHz, 16-bit mono
    speech = [InputAudioRawFrame(audio=pcm[i:i + chunk], sample_rate=16000, num_channels=1) for i in range(0, len(pcm) - chunk, chunk)]
    silence = [InputAudioRawFrame(audio=b"\x00" * chunk, sample_rate=16000, num_channels=1) for _ in range(100)]   # 2 s of quiet ends the sentence
    return speech + silence


@pytest.mark.skipif(not CLIP.exists(), reason="needs the founder's local recording (kept out of git)")
def test_a_spoken_sentence_goes_in_and_a_spoken_answer_comes_out():
    stt_provider, tts_provider = FakeSTT("my laptop charger stopped working"), WavTTS()
    chain = Pipeline([
        VADProcessor(vad_analyzer=SileroVADAnalyzer()),
        NivaranSTTService(stt_provider, language_hint="en-IN"),
        Echo("en-IN"),
        NivaranTTSService(tts_provider, locale="en-IN"),
    ])
    down, _ = asyncio.run(run_test(chain, frames_to_send=_frames(CLIP), ignore_start=True))
    kinds = [type(f) for f in down]
    assert TTSAudioRawFrame in kinds, f"no spoken answer; got {sorted({k.__name__ for k in kinds})}"
    assert stt_provider.calls, "speech-to-text was never called: the voice detector did not find the sentence"
    assert stt_provider.calls[0][2] == "en-IN"
    assert tts_provider.calls[0][0] == "You said: my laptop charger stopped working"
