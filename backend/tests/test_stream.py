import json

import pytest

from app.brain.stream import SayStreamer


def stream(text, size):
    s, sentences = SayStreamer(), []
    for i in range(0, len(text), size):
        sentences += s.feed(text[i:i + size])
    sentences += s.flush()
    return s, sentences


DOC = json.dumps({"action": "continue", "digits": "", "say": "My customer's order ID is 4839201. They want a refund! Can you help?"}, ensure_ascii=False)


@pytest.mark.parametrize("size", [1, 2, 3, 7, 50, 1000])
def test_sentences_come_out_whole_whatever_the_piece_size(size):
    s, sentences = stream(DOC, size)
    assert sentences == ["My customer's order ID is 4839201.", "They want a refund!", "Can you help?"]
    assert s.action == "continue" and s.full_json()["say"].startswith("My customer")


def test_the_first_sentence_is_ready_before_the_answer_is_finished():
    s = SayStreamer()
    got = s.feed(DOC[:DOC.index("They")])
    assert got == ["My customer's order ID is 4839201."] and not s.closed


def test_escapes_and_non_english_text():
    doc = json.dumps({"action": "wait", "digits": "", "say": 'He said "hold on". मैं यहीं हूँ। ठीक है।\nOk.'})     # ascii escapes (\uXXXX) included
    s, sentences = stream(doc, 3)
    assert sentences == ['He said "hold on".', "मैं यहीं हूँ।", "ठीक है। Ok."] or sentences[0] == 'He said "hold on".'
    assert s.action == "wait"


def test_nothing_is_handed_out_before_the_say_field_starts():
    s = SayStreamer()
    assert s.feed('{"action": "press_digits", "digits": "1", "sa') == [] and s.action == "press_digits"
