import pytest

from app.safety.redact import redact, scrub

CARDS = [
    "4111 1111 1111 1111",      # Visa test number, spaced
    "4111-1111-1111-1111",      # dashed
    "4012888888881881",         # contiguous, Luhn valid
    "5555 5555 5555 4444",      # Mastercard test number
    "3782 822463 10005",        # Amex layout
    "1234 5678 9012 3456",      # bad Luhn but a normal card layout: still removed
]


@pytest.mark.parametrize("card", CARDS)
def test_card_numbers_are_removed(card):
    clean, kinds = redact(f"my card is {card} please help")
    digits = "".join(c for c in clean if c.isdigit())
    assert "card_number" in kinds
    assert digits == ""
    assert "[CARD NUMBER REMOVED]" in clean


@pytest.mark.parametrize("text", [
    "Order 402-5539281-1129384",       # Amazon-style id
    "OD10894537621345",                # Flipkart-style id glued to letters
    "PNR 4521896307",                  # 10 digits
    "call me on +91 98765 43210",      # phone number
    "Rs 599 deducted on 12 October",
])
def test_ordinary_numbers_are_kept(text):
    clean, kinds = redact(text)
    assert clean == text
    assert kinds == []


def test_cvv_and_pin_are_removed():
    clean, kinds = redact("cvv is 123 and my UPI PIN: 482913")
    assert "123" not in clean and "482913" not in clean
    assert set(kinds) == {"cvv", "pin"}


def test_scrub_cleans_nested_ai_answer():
    answer = {"a": ["card 4111 1111 1111 1111"], "b": {"c": "fine"}}
    clean, kinds = scrub(answer)
    assert "4111" not in str(clean)
    assert kinds == ["card_number"]
