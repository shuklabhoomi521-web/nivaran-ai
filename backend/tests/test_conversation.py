from app.brain.speak import FALLBACK, spoken_summary
from app.voice.conversation import APOLOGY, GREETING, HOW, MAX_QUESTIONS, Conversation
from tests.conftest import FakeLLM, case_dict


class ScriptedLLM:
    """Gives the next canned answer each time (understand, plan, spoken summary in order)."""

    def __init__(self, *answers):
        self.answers, self.calls = list(answers), []

    def complete_json(self, *, system, user, schema):
        self.calls.append({"system": system, "user": user})
        return self.answers.pop(0)


PLAN = {"channel": "email", "reason": "no phone line", "opening_line": "Hello, writing about an order.", "proof_to_keep": ["photo"]}


def test_missing_company_makes_the_assistant_ask_one_question_and_not_finish():
    llm = ScriptedLLM(case_dict(company=None, details_known=[], details_missing=["company"], follow_up_question="Which company is this about?", reply_language="en-IN", spoken_reply="x"))
    conv = Conversation("en-IN", llm)
    t = conv.handle("my food came cold")
    assert t.reply == "Which company is this about?" and not conv.finished and conv.questions_asked == 1


def test_complete_case_ends_with_a_short_confirmation_and_nothing_is_sent():
    llm = ScriptedLLM(case_dict(reply_language="en-IN", spoken_reply="Your Swiggy order came cold and you want a refund."))
    conv = Conversation("en-IN", llm)
    t = conv.handle("Swiggy order 4839201 came cold, I want a refund")
    assert conv.finished and "nothing has been sent" in t.reply.lower()
    assert "channel=" in t.note and "company=Swiggy" in t.note


def test_the_second_answer_is_added_to_the_first_before_understanding():
    llm = ScriptedLLM(
        case_dict(company=None, details_known=[], details_missing=["company"], follow_up_question="Which company?", reply_language="en-IN", spoken_reply="x"),
        case_dict(reply_language="en-IN", spoken_reply="Done."))
    conv = Conversation("en-IN", llm)
    conv.handle("my food came cold")
    conv.handle("Swiggy")
    assert "my food came cold" in llm.calls[1]["user"] and "LAST MESSAGE" in llm.calls[1]["user"] and "Swiggy" in llm.calls[1]["user"]


def test_card_number_said_aloud_never_reaches_the_ai_or_comes_back():
    llm = ScriptedLLM(case_dict(reply_language="en-IN", spoken_reply="I paid with card 4111 1111 1111 1111 so I will email Swiggy."))
    conv = Conversation("en-IN", llm)
    t = conv.handle("Swiggy refund please, my card is 4111 1111 1111 1111")
    assert "4111" not in llm.calls[0]["user"]          # removed before the AI saw it
    assert "4111" not in t.reply                        # and cleaned from what we speak


def test_spoken_card_number_with_a_transcription_slip_is_removed_before_the_ai():
    llm = ScriptedLLM(case_dict(reply_language="en-IN", spoken_reply="I will email Swiggy."))
    conv = Conversation("en-IN", llm)
    conv.handle("Swiggy refund please my card number is 4111111111111111111")
    assert "4111" not in llm.calls[0]["user"] and "[CARD NUMBER REMOVED]" in llm.calls[0]["user"]


def test_company_not_in_the_directory_cannot_proceed_and_says_so():
    llm = ScriptedLLM(case_dict(company="Nonexistent Foods", reply_language="en-IN", spoken_reply="Cold food from Nonexistent Foods."))
    conv = Conversation("en-IN", llm)
    t = conv.handle("Nonexistent Foods sent me cold food")
    assert conv.finished and "cannot reach this company" in t.reply and "Nothing has been sent" in t.reply


def test_stops_asking_after_too_many_questions():
    q = case_dict(company=None, details_known=[], details_missing=["company"], follow_up_question="Which company?", reply_language="en-IN", spoken_reply="x")
    llm = ScriptedLLM(*([q] * MAX_QUESTIONS), case_dict(reply_language="en-IN", spoken_reply="Summary."))
    conv = Conversation("en-IN", llm)
    for _ in range(MAX_QUESTIONS):
        assert conv.handle("hmm").reply == "Which company?"
    assert conv.handle("hmm").reply.startswith("Summary.") and conv.finished


def test_each_language_has_a_greeting_and_a_fallback():
    assert set(GREETING) == {"auto", "en-IN", "hi-IN", "ta-IN", "hinglish"}
    assert set(FALLBACK) == {"english", "hindi", "tamil", "hinglish"}


def test_spoken_summary_falls_back_when_the_ai_answer_is_broken():
    assert spoken_summary({}, {"channel": "email"}, "hindi", FakeLLM({"nonsense": 1})) == FALLBACK["hindi"]


def test_every_language_has_an_apology_and_a_sentence_for_each_way_of_contact():
    assert set(APOLOGY) == set(HOW) == {"en-IN", "hi-IN", "ta-IN", "hinglish"}
    for lang, ways in HOW.items():
        assert set(ways) == {"call", "email", "complaint", None}


def test_the_whole_turn_is_one_ai_call():
    llm = ScriptedLLM(case_dict(reply_language="en-IN", spoken_reply="Swiggy refund."))
    Conversation("en-IN", llm).handle("Swiggy order came cold, refund please")
    assert len(llm.calls) == 1


def test_a_slow_answer_that_arrives_after_a_rewind_changes_nothing():
    llm = ScriptedLLM(case_dict(reply_language="en-IN", spoken_reply="Late."))
    conv = Conversation("en-IN", llm)
    snap = conv.snapshot()
    real = llm.complete_json

    def slow(**kw):
        conv.restore(snap)             # we gave up and rewound while the AI was still thinking
        return real(**kw)
    llm.complete_json = slow
    conv.handle("Swiggy refund")
    assert not conv.finished and conv.turns == [] and conv.texts == []


def test_the_bot_follows_the_user_when_they_switch_language_mid_chat():
    llm = ScriptedLLM(
        case_dict(company=None, details_known=[], details_missing=["company"], follow_up_question="Which company?", reply_language="en-IN", spoken_reply="x"),
        case_dict(company="Zomato", reply_language="hi-IN", spoken_reply="आपका ज़ोमैटो का खाना ठंडा था।"))
    conv = Conversation("auto", llm)
    first = conv.handle("my food came cold")
    assert first.language == "en-IN" and conv.language == "en-IN"
    second = conv.handle("zomato, पैसे वापस चाहिए")
    assert second.language == "hi-IN" and conv.language == "hi-IN"
    assert "ज़ोमैटो" in second.reply and HOW["hi-IN"]["email"].split("{c}")[0] in second.reply or "कुछ" in second.reply   # our second sentence is Hindi too
    assert "Nothing has been sent" not in second.reply


def test_auto_mode_greets_in_every_language_and_the_brain_is_told_to_follow_the_last_message():
    from app.brain.understand import VOICE_ADDON
    assert "auto" in GREETING and "LAST message" in VOICE_ADDON


def test_talking_after_the_summary_is_still_answered_and_in_the_new_language():
    llm = ScriptedLLM(
        case_dict(reply_language="en-IN", spoken_reply="Swiggy refund."),
        case_dict(reply_language="hi-IN", spoken_reply="स्विगी रिफंड।"))
    conv = Conversation("auto", llm)
    conv.handle("Swiggy order came late, refund")
    assert conv.finished
    t = conv.handle("मेरा order number 481520 है")
    assert t.language == "hi-IN" and "स्विगी" in t.reply and len(llm.calls) == 2
    assert "LAST MESSAGE" in llm.calls[1]["user"]
