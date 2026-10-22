from app.brain.speak import FALLBACK, spoken_summary
from app.voice.conversation import GREETING, MAX_QUESTIONS, Conversation
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
    llm = ScriptedLLM(case_dict(company=None, details_known=[], details_missing=["company"], follow_up_question="Which company is this about?"))
    conv = Conversation("en-IN", llm)
    t = conv.handle("my food came cold")
    assert t.reply == "Which company is this about?" and not conv.finished and conv.questions_asked == 1


def test_complete_case_ends_with_a_short_confirmation_and_nothing_is_sent():
    llm = ScriptedLLM(case_dict(), {"reply": "Your Swiggy order came cold and you want a refund. I would send a complaint email; nothing has been sent yet."})
    conv = Conversation("en-IN", llm)
    t = conv.handle("Swiggy order 4839201 came cold, I want a refund")
    assert conv.finished and "nothing has been sent" in t.reply
    assert "channel=" in t.note and "company=Swiggy" in t.note


def test_the_second_answer_is_added_to_the_first_before_understanding():
    llm = ScriptedLLM(
        case_dict(company=None, details_known=[], details_missing=["company"], follow_up_question="Which company?"),
        case_dict(), {"reply": "Done."})
    conv = Conversation("en-IN", llm)
    conv.handle("my food came cold")
    conv.handle("Swiggy")
    assert "my food came cold" in llm.calls[1]["user"] and "Swiggy" in llm.calls[1]["user"]


def test_card_number_said_aloud_never_reaches_the_ai_or_comes_back():
    llm = ScriptedLLM(case_dict(), {"reply": "I paid with card 4111 1111 1111 1111 so I will email Swiggy."})
    conv = Conversation("en-IN", llm)
    t = conv.handle("Swiggy refund please, my card is 4111 1111 1111 1111")
    assert "4111" not in llm.calls[0]["user"]          # removed before the AI saw it
    assert "4111" not in t.reply                        # and cleaned from what we speak


def test_spoken_card_number_with_a_transcription_slip_is_removed_before_the_ai():
    llm = ScriptedLLM(case_dict(), {"reply": "I will email Swiggy."})
    conv = Conversation("en-IN", llm)
    conv.handle("Swiggy refund please my card number is 4111111111111111111")
    assert "4111" not in llm.calls[0]["user"] and "[CARD NUMBER REMOVED]" in llm.calls[0]["user"]


def test_company_not_in_the_directory_cannot_proceed_and_says_so():
    llm = ScriptedLLM(case_dict(company="Nonexistent Foods"), {"reply": "I cannot reach this company yet. Nothing has been sent."})
    conv = Conversation("en-IN", llm)
    t = conv.handle("Nonexistent Foods sent me cold food")
    assert conv.finished and "not in the verified directory" in llm.calls[-1]["user"]
    assert "Nothing has been sent" in t.reply


def test_stops_asking_after_too_many_questions():
    q = case_dict(company=None, details_known=[], details_missing=["company"], follow_up_question="Which company?")
    llm = ScriptedLLM(*([q] * MAX_QUESTIONS), q, {"reply": "Summary."})
    conv = Conversation("en-IN", llm)
    for _ in range(MAX_QUESTIONS):
        assert conv.handle("hmm").reply == "Which company?"
    assert conv.handle("hmm").reply == "Summary." and conv.finished


def test_each_language_has_a_greeting_and_a_fallback():
    assert set(GREETING) == {"en-IN", "hi-IN", "ta-IN", "hinglish"}
    assert set(FALLBACK) == {"english", "hindi", "tamil", "hinglish"}


def test_spoken_summary_falls_back_when_the_ai_answer_is_broken():
    assert spoken_summary({}, {"channel": "email"}, "hindi", FakeLLM({"nonsense": 1})) == FALLBACK["hindi"]
