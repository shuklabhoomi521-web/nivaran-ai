"""Voice chain with the real conversation logic: a recorded sentence goes in, the bot asks the next question out loud.
Fake speech providers and a scripted AI: no network, no microphone."""
import asyncio

import pytest
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import TTSAudioRawFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.processors.audio.vad_processor import VADProcessor
from pipecat.tests.utils import run_test

from app.speech.fakes import FakeSTT
from app.voice.conversation import Conversation
from app.voice.services import NivaranSTTService, NivaranTTSService
from app.voice.voice_bot import ConversationProcessor
from tests.conftest import case_dict
from tests.test_conversation import ScriptedLLM
from tests.test_voice_pipeline import CLIP, _frames
from tests.test_voice_services import WavTTS


@pytest.mark.skipif(not CLIP.exists(), reason="needs the founder's local recording (kept out of git)")
def test_spoken_problem_with_no_company_gets_a_spoken_question():
    llm = ScriptedLLM(case_dict(company=None, details_known=[], details_missing=["company"], follow_up_question="Which company is this about?"))
    tts = WavTTS()
    stt = NivaranSTTService(FakeSTT("my laptop charger stopped working"), language_hint="en-IN")
    chain = Pipeline([VADProcessor(vad_analyzer=SileroVADAnalyzer()), stt, ConversationProcessor(Conversation("en-IN", llm), stt),
                      NivaranTTSService(tts, locale="en-IN")])
    down, _ = asyncio.run(run_test(chain, frames_to_send=_frames(CLIP), ignore_start=True))
    assert any(isinstance(f, TTSAudioRawFrame) for f in down)
    assert tts.calls[0][0] == "Which company is this about?"
