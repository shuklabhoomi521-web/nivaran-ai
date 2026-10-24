import pytest

from app.voice.call_conversation import (DISCLOSURE, GOODBYE, NEED_USER, REFUSE_SECRET, CallConversation)

CASE = {"company": "Swiggy", "problem_summary": "Order arrived cold; no refund.", "user_goal": "refund",
        "details_known": [{"name": "order_id", "value": "4839201"}]}


class Scripted:
    def __init__(self, *answers):
        self.answers, self.calls = list(answers), []

    def complete_json(self, *, system, user, schema):
        self.calls.append(user)
        return self.answers.pop(0)


def turn(say, action="continue", digits=""):
    return {"say": say, "action": action, "digits": digits}


@pytest.mark.parametrize("lang", ["en-IN", "hi-IN", "ta-IN", "hinglish"])
def test_the_first_words_are_always_the_ai_disclosure_in_every_language(lang):
    c = CallConversation(CASE, lang, Scripted())
    first = c.opening()
    assert "AI" in first and "Swiggy" in first and first == DISCLOSURE[lang].format(company="Swiggy")
    assert not c.llm.calls                          # fixed text: the AI does not write it


def test_the_ai_never_pretends_to_be_the_customer_in_its_instructions():
    from app.voice.call_conversation import SYSTEM_PROMPT
    assert "NOT the customer" in SYSTEM_PROMPT and "Never invent" in SYSTEM_PROMPT


@pytest.mark.parametrize("ask", ["Please tell me the OTP you received", "What is your card number?", "Say your CVV", "Give me your PIN",
                                 "आपका ओटीपी क्या है", "कार्ड नंबर बताइए", "கார்டு எண் சொல்லுங்கள்"])
def test_when_the_agent_asks_for_a_secret_we_refuse_in_fixed_words_and_do_not_ask_the_ai(ask):
    llm = Scripted()
    c = CallConversation(CASE, "en-IN", llm)
    c.opening()
    assert c.respond(ask) == REFUSE_SECRET["en-IN"] and not llm.calls


def test_normal_turn_uses_one_ai_call_and_only_known_facts():
    llm = Scripted(turn("My customer's order ID is 4839201. They want a refund."))
    c = CallConversation(CASE, "en-IN", llm)
    c.opening()
    assert "4839201" in c.respond("How can I help you?") and len(llm.calls) == 1 and "4839201" in llm.calls[0]


def test_a_card_number_in_the_ai_answer_is_removed():
    llm = Scripted(turn("They paid with card 4111 1111 1111 1111 for the order."))
    c = CallConversation(CASE, "en-IN", llm)
    c.opening()
    assert "4111" not in c.respond("What was the payment method?")


def test_an_ai_that_asks_the_agent_for_an_otp_is_replaced_by_the_refusal():
    llm = Scripted(turn("Please send the OTP to this number."))
    c = CallConversation(CASE, "en-IN", llm)
    c.opening()
    assert c.respond("Anything else?") == REFUSE_SECRET["en-IN"]


def test_menu_choice_presses_digits_and_only_digits():
    llm = Scripted(turn("Pressing one.", "press_digits", "1 #"))
    c = CallConversation(CASE, "en-IN", llm)
    c.opening()
    c.respond("Press 1 for orders, 2 for payments")
    assert c.last_action == "press_digits" and c.last_digits == "1#"


def test_press_digits_without_digits_becomes_a_normal_turn():
    c = CallConversation(CASE, "en-IN", Scripted(turn("One moment.", "press_digits", "abc")))
    c.opening(); c.respond("menu")
    assert c.last_action == "continue" and c.last_digits == ""


def test_missing_fact_asks_the_user_and_hold_waits():
    c = CallConversation(CASE, "en-IN", Scripted(turn("I do not have the phone number.", "need_user"), turn("Thank you.", "wait")))
    c.opening()
    c.respond("What is the registered phone number?")
    assert c.last_action == "need_user"
    c.respond("Please hold")
    assert c.last_action == "wait"


def test_goodbye_ends_the_call():
    c = CallConversation(CASE, "en-IN", Scripted(turn("Thank you, goodbye.", "end_call")))
    c.opening(); c.respond("Your ticket is T-55. Anything else?")
    assert c.ended and c.last_action == "end_call"


def test_a_broken_ai_never_leaves_silence_on_the_phone():
    class Broken:
        def complete_json(self, **kw):
            raise RuntimeError("down")
    c = CallConversation(CASE, "hi-IN", Broken())
    c.opening()
    assert c.respond("नमस्ते") == NEED_USER["hi-IN"] and c.last_action == "need_user"


def test_a_call_cannot_go_on_forever():
    c = CallConversation(CASE, "en-IN", Scripted(*[turn("ok")] * 20))
    c.max_turns = 3
    c.opening()
    for _ in range(5):
        if c.ended:
            break
        c.respond("hmm")
    assert c.ended and c.history[-1][1] == GOODBYE["en-IN"]
