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
    llm = ScriptedLLM(case_dict(company=None, details_known=[], details_missing=["company"], follow_up_question="Which company is this about?", spoken_reply="x"))
    tts = WavTTS()
    stt = NivaranSTTService(FakeSTT("my laptop charger stopped working"), language_hint="en-IN")
    chain = Pipeline([VADProcessor(vad_analyzer=SileroVADAnalyzer()), stt, ConversationProcessor(Conversation("en-IN", llm), stt),
                      NivaranTTSService(tts, locale="en-IN")])
    down, _ = asyncio.run(run_test(chain, frames_to_send=_frames(CLIP), ignore_start=True))
    assert any(isinstance(f, TTSAudioRawFrame) for f in down)
    assert tts.calls[0][0] == "Which company is this about?"


def test_two_quick_sentences_are_answered_together_and_the_stale_answer_is_dropped():
    import time

    from pipecat.frames.frames import TTSSpeakFrame

    from app.voice.voice_bot import ConversationProcessor

    class SlowLLM(ScriptedLLM):
        def complete_json(self, **kw):
            time.sleep(0.4)
            return super().complete_json(**kw)

    q = lambda t: case_dict(company=None, details_known=[], details_missing=["company"], follow_up_question=t, spoken_reply="x")  # noqa: E731
    llm = SlowLLM(q("STALE question?"), q("Which company, please?"))
    proc = ConversationProcessor(Conversation("en-IN", llm), NivaranSTTService(FakeSTT("x")))
    spoken = []

    async def capture(frame, direction=None):
        spoken.append(frame)
    proc.push_frame = capture

    async def go():
        proc._pending.append("my food came cold")
        worker = asyncio.create_task(proc._think())
        await asyncio.sleep(0.15)                       # while the AI is still thinking about the first sentence...
        proc._pending.append("and I want a refund")     # ...the person keeps talking
        await worker

    asyncio.run(go())
    texts = [f.text for f in spoken if isinstance(f, TTSSpeakFrame)]
    assert texts == ["Which company, please?"], texts   # one answer; the stale one was never spoken
    assert "my food came cold and I want a refund" in llm.calls[-1]["user"]
    assert proc._conv.questions_asked == 1              # the dropped turn did not count as a question


def test_slow_thinking_says_one_moment():
    import time

    from pipecat.frames.frames import TTSSpeakFrame

    from app.voice.voice_bot import ConversationProcessor

    class SlowLLM(ScriptedLLM):
        def complete_json(self, **kw):
            time.sleep(0.5)
            return super().complete_json(**kw)

    llm = SlowLLM(case_dict(company=None, details_known=[], details_missing=["company"], follow_up_question="Which company?", spoken_reply="x"))
    proc = ConversationProcessor(Conversation("en-IN", llm), NivaranSTTService(FakeSTT("x")))
    proc.SLOW_AFTER = 0.1
    spoken = []

    async def capture(frame, direction=None):
        spoken.append(frame)
    proc.push_frame = capture

    async def go():
        proc._pending.append("hello")
        await proc._think()

    asyncio.run(go())
    assert [f.text for f in spoken if isinstance(f, TTSSpeakFrame)] == ["One moment, please.", "Which company?"]


def test_when_the_brain_fails_the_bot_apologises_in_the_users_language_and_never_goes_silent():
    from pipecat.frames.frames import TTSSpeakFrame

    from app.voice.conversation import APOLOGY

    class Broken:
        def complete_json(self, **kw):
            raise RuntimeError("AI is down")

    proc = ConversationProcessor(Conversation("hi-IN", Broken()), NivaranSTTService(FakeSTT("x")))
    spoken = []

    async def capture(frame, direction=None):
        spoken.append(frame)
    proc.push_frame = capture

    async def go():
        proc._pending.append("namaste")
        await proc._think()
    asyncio.run(go())
    assert [f.text for f in spoken if isinstance(f, TTSSpeakFrame)] == [APOLOGY["hi-IN"]]


def test_a_brain_that_takes_too_long_gets_an_apology_too():
    import time

    from pipecat.frames.frames import TTSSpeakFrame

    from app.voice.conversation import APOLOGY

    class Stuck:
        def complete_json(self, **kw):
            time.sleep(1.0)
            return case_dict(spoken_reply="late")

    proc = ConversationProcessor(Conversation("en-IN", Stuck()), NivaranSTTService(FakeSTT("x")))
    proc.BRAIN_DEADLINE, proc.SLOW_AFTER = 0.2, 99
    spoken = []

    async def capture(frame, direction=None):
        spoken.append(frame)
    proc.push_frame = capture

    async def go():
        proc._pending.append("hello")
        await proc._think()
    asyncio.run(go())
    assert [f.text for f in spoken if isinstance(f, TTSSpeakFrame)] == [APOLOGY["en-IN"]]
    assert not proc._conv.finished


def test_a_final_answer_is_spoken_one_sentence_at_a_time():
    from app.voice.voice_bot import split_sentences
    assert split_sentences("Swiggy refund. I can email Swiggy! Nothing sent.") == ["Swiggy refund.", "I can email Swiggy!", "Nothing sent."]
    assert split_sentences("मैं समझ गया। कुछ नहीं भेजा।") == ["मैं समझ गया।", "कुछ नहीं भेजा।"]
