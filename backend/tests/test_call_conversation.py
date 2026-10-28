import re
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


def turn(say, action="continue", digits="", lang="en-IN"):
    return {"say": say, "action": action, "digits": digits, "reply_language": lang}


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
    lang = "hi-IN" if re.search(r"[\u0900-\u097F]", ask) else "ta-IN" if re.search(r"[\u0B80-\u0BFF]", ask) else "en-IN"
    assert c.respond(ask) == REFUSE_SECRET[lang] and not llm.calls          # the refusal is in the agent's own language


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


class Streaming:
    """An AI that writes its answer in pieces; `seen` records how many sentences had been handed out when the last piece was written."""

    def __init__(self, doc, size=6):
        self.doc, self.size, self.seen_at_end = doc, size, None
        self.sentences = None

    def stream_json(self, *, system, user, schema):
        import json
        text = json.dumps(self.doc, ensure_ascii=False)
        pieces = [text[i:i + self.size] for i in range(0, len(text), self.size)]
        for n, piece in enumerate(pieces):
            if n == len(pieces) - 1:
                self.seen_at_end = len(self.sentences)
            yield piece

    def complete_json(self, **kw):
        return self.doc


def test_speaking_starts_before_the_ai_has_finished_writing():
    ai = Streaming({"action": "continue", "digits": "", "reply_language": "en-IN", "say": "My customer's order ID is 4839201. They want a refund. Thank you."})
    c = CallConversation(CASE, "en-IN", ai)
    c.opening()
    said = ai.sentences = []
    reply = c.respond("How can I help?", said.append)
    assert said == ["My customer's order ID is 4839201.", "They want a refund.", "Thank you."]
    assert ai.seen_at_end >= 2 and c.streamed and reply.startswith("My customer")


def test_a_key_press_is_never_spoken_even_when_streaming():
    ai = Streaming({"action": "press_digits", "digits": "1", "reply_language": "en-IN", "say": "Pressing one."})
    c = CallConversation(CASE, "en-IN", ai)
    c.opening(); said = ai.sentences = []
    c.respond("Press 1 for orders", said.append)
    assert said == [] and c.last_action == "press_digits" and c.last_digits == "1"


def test_a_secret_is_never_streamed_out():
    ai = Streaming({"action": "continue", "digits": "", "reply_language": "en-IN", "say": "Sure. Please share the OTP now. Thanks."})
    c = CallConversation(CASE, "en-IN", ai)
    c.opening(); said = ai.sentences = []
    c.respond("Anything else?", said.append)
    assert said == ["Sure."]                       # the sentence asking for an OTP and everything after it were held back


def test_streaming_text_is_cleaned_like_normal_text():
    ai = Streaming({"action": "continue", "digits": "", "reply_language": "en-IN", "say": "They paid with card 4111 1111 1111 1111. Thanks."})
    c = CallConversation(CASE, "en-IN", ai)
    c.opening(); said = ai.sentences = []
    c.respond("How did they pay?", said.append)
    assert all("4111" not in s for s in said)


def test_a_stream_that_breaks_midway_does_not_add_a_second_confusing_sentence():
    class Breaks(Streaming):
        def stream_json(self, **kw):
            yield '{"action": "continue", "digits": "", "reply_language": "en-IN", "say": "First sentence. Sec'
            raise RuntimeError("connection lost")
    ai = Breaks({})
    c = CallConversation(CASE, "en-IN", ai)
    c.opening(); said = ai.sentences = []
    assert c.respond("hello", said.append) == "" and said == ["First sentence."]


def test_a_key_press_with_no_words_is_a_key_press_not_a_missing_fact():
    c = CallConversation(CASE, "en-IN", Scripted({"action": "press_digits", "digits": "1", "reply_language": "en-IN", "say": ""}))
    c.opening()
    assert c.respond("Press 1 for orders") == "" and c.last_action == "press_digits" and c.last_digits == "1"


def test_the_ai_follows_the_agent_into_another_language_even_while_streaming():
    ai = Streaming({"action": "continue", "digits": "", "reply_language": "hi-IN", "say": "जी, ऑर्डर नंबर 4839201 है। कृपया रिफंड कर दीजिए।"})
    c = CallConversation(CASE, "en-IN", ai)
    c.opening(); said = ai.sentences = []
    c.respond("जी बताइए, क्या समस्या है?", said.append)
    assert c.language == "hi-IN" and said[0].startswith("जी, ऑर्डर")
    assert c._fixed(REFUSE_SECRET) == REFUSE_SECRET["hi-IN"]          # fixed sentences switch too


# ---- the Hindi bug: the agent speaks Hindi, the AI must answer in Devanagari (or proper hinglish when the call is set up as hinglish)
def test_the_prompt_tells_the_ai_which_script_to_use():
    from app.voice.call_conversation import SYSTEM_PROMPT
    assert "language_setting" in SYSTEM_PROMPT and "Devanagari" in SYSTEM_PROMPT and "hinglish ONLY when" in SYSTEM_PROMPT


def test_roman_hindi_from_the_agent_is_answered_as_hindi_unless_the_call_is_set_up_as_hinglish():
    for setting, expected in (("en-IN", "hi-IN"), ("hi-IN", "hi-IN"), ("hinglish", "hinglish")):
        ai = Scripted(turn("जी, ऑर्डर नंबर 4839201 है।" if expected == "hi-IN" else "Ji, order number 4839201 hai.", lang="hinglish"))
        c = CallConversation(CASE, setting, ai)
        c.opening(); c.respond("Namaste, main priya bol rahi hoon. Bataiye kya samasya hai?")
        assert c.language == expected, (setting, c.language)


def test_the_payload_carries_the_language_setting():
    ai = Scripted(turn("ok"))
    c = CallConversation(CASE, "hi-IN", ai)
    c.opening(); c.respond("hello")
    assert '"language_setting": "hi-IN"' in ai.calls[0]


def test_hindi_written_in_english_letters_is_rewritten_into_devanagari_once():
    class Two:
        calls = 0

        def complete_json(self, *, system, user, schema):
            Two.calls += 1
            if "text" in schema.get("properties", {}):                       # the rewrite request
                return {"text": "जी, ऑर्डर नंबर 4839201 है।"}
            return turn("Ji, order number 4839201 hai, refund chahiye.", lang="hi-IN")
    c = CallConversation(CASE, "hi-IN", Two())
    c.opening()
    reply = c.respond("नमस्ते, बताइए क्या समस्या है?")
    assert re.search(r"[ऀ-ॿ]", reply) and "4839201" in reply and Two.calls == 2


def test_if_the_rewrite_fails_the_original_words_are_kept_not_lost():
    class Broken:
        def complete_json(self, *, system, user, schema):
            if "text" in schema.get("properties", {}):
                raise RuntimeError("down")
            return turn("Ji, order number 4839201 hai, refund chahiye.", lang="hi-IN")
    c = CallConversation(CASE, "hi-IN", Broken())
    c.opening()
    assert "4839201" in c.respond("नमस्ते")


def test_streamed_hindi_sentences_are_checked_for_script_before_they_are_spoken():
    class Streams(Streaming):
        def complete_json(self, **kw):
            return {"text": "जी, ऑर्डर नंबर 4839201 है।"}
    ai = Streams({"action": "continue", "digits": "", "reply_language": "hi-IN", "say": "Ji, order number 4839201 hai, refund chahiye."})
    c = CallConversation(CASE, "hi-IN", ai)
    c.opening(); said = ai.sentences = []
    c.respond("नमस्ते", said.append)
    assert said and re.search(r"[ऀ-ॿ]", said[0])


def test_the_agents_language_is_detected_in_code_from_script_and_common_words():
    d = CallConversation.detect_language
    assert d("नमस्ते, बताइए क्या समस्या है?") == "hi-IN" and d("வணக்கம், என்ன பிரச்சனை?") == "ta-IN"
    assert d("Namaste, main priya bol rahi hoon. Bataiye kya samasya hai?") == "hi-IN"
    assert d("Hello, this is Priya from Swiggy support. How can I help you?") is None
    assert d("Please hold, ji") is None                      # one stray word is not enough


def test_when_the_agent_speaks_hindi_the_ai_answers_in_hindi_even_if_the_call_started_in_english_and_the_ai_picks_english():
    ai = Scripted(turn("जी, ऑर्डर नंबर 4839201 है।", lang="en-IN"))           # the AI wrongly says en-IN
    c = CallConversation(CASE, "en-IN", ai)
    c.opening()
    reply = c.respond("Namaste, main priya bol rahi hoon. Bataiye kya samasya hai?")
    assert c.language == "hi-IN" and re.search(r"[ऀ-ॿ]", reply)
    assert '"language": "hi-IN"' in ai.calls[0]                                # the AI was already told Hindi


def test_hinglish_setting_keeps_roman_letters_when_the_agent_speaks_hindi():
    ai = Scripted(turn("Ji, order number 4839201 hai.", lang="hinglish"))
    c = CallConversation(CASE, "hinglish", ai)
    c.opening(); c.respond("Namaste, main priya bol rahi hoon. Bataiye kya samasya hai?")
    assert c.language == "hinglish"                 # a call set up as hinglish stays in English letters
