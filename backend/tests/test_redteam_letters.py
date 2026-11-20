"""Red team: 50 tricky messages put into a case as a 'fact', then pushed through the letter writer and the portal kit.
BLOCKED = payment data that must never reach a letter. ALLOWED = ordinary details that must still work.
KNOWN_GAPS are attacks we do NOT catch yet: they are listed on purpose (strict xfail), so a fix turns them into a loud test result."""
from datetime import date

import pytest

from app.cases import engine
from app.cases.kit import build_kit
from app.letters.compose import LetterError, compose
from app.models.case import Case, Category, Confidence, Fact, Language, Urgency, UserGoal

D0 = date(2026, 12, 5)

BLOCKED = [
    "my card is 4111 1111 1111 1111", "card number 4111-1111-1111-1111", "4111111111111111 was charged", "visa 4012 8888 8888 1881",
    "mastercard 5555 5555 5555 4444 expired", "Amex 3782 822463 10005", "rupay 6521 1234 5678 9012", "paid with 5105105105105100",
    "cvv is 123", "CVV: 4567", "cvv2 987", "cvc 999", "the cvv number is 321",
    "upi pin 4829", "UPI PIN: 2468", "my atm pin is 1234", "ATM PIN 9876", "pin 123456", "pin is 4321",
    "card ४१११ १११९ १११९ १११९ number", "card ٤١١١ ١١١١ ١١١١ ١١١١", "card １２３４ ５６７８ ９０１２ ３４５６",
    "Hi, my card 4111 1111 1111 1111 and cvv 123 please refund", "refund to 4111 1111 1111 1111 (cvv 123, pin 4829)",
    "ORDER 4839201. also my pin 5821 for UPI", "line one\nline two card 4111 1111 1111 1111\nline three",
    "CARD 4111 1111 1111 1111", "Card No.: 4111 1111 1111 1111.", "card:4111 1111 1111 1111;", "pin 7788 and cvv 456",
    "4111.1111.1111.1111", "card 4 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1",
]

ALLOWED = [
    "order id 4839201", "phone 9876543210", "refund of Rs 1,375.00", "booking PNR 2345678901", "complaint number BB-90417",
    "delivery on 2026-12-05", "my flat is on the 4th floor", "ticket TKT-77 was created", "paid 250 rupees by UPI", "the app crashed 3 times",
]

KNOWN_GAPS = [
    "card number is four one one one one one one one one one one one one one one one",
    "cvv is one two three",
    "my card 4111 x 1111 x 1111 x 1111",
    "pin is four eight two nine",

]


def case(fact_text: str):
    u = Case(company="Swiggy", category=Category.food_delivery, category_confidence=Confidence.high, problem_summary="Refund not given.",
             user_goal=UserGoal.refund, details_known=[Fact(name="note", value=fact_text)], details_missing=[], user_language=Language.english,
             urgency=Urgency.low, other_issues=[])
    return engine.new_case(u, D0, "r1", user_name="Tester")


def test_there_are_50_attacks_in_the_list():
    assert len(BLOCKED) + len(ALLOWED) + len(KNOWN_GAPS) >= 46


@pytest.mark.parametrize("text", BLOCKED)
def test_payment_data_is_blocked_in_letters_and_kits(text):
    c = case(text)
    action = engine.next_action(c, D0, None)
    # the first-contact letter needs a verified target, so test with Swiggy's real directory entry
    from app.directory.lookup import find_company
    action = engine.next_action(c, D0, find_company("Swiggy"))
    with pytest.raises(LetterError):
        compose(c, action, D0)
    with pytest.raises(LetterError):
        build_kit(c, D0)


@pytest.mark.parametrize("text", ALLOWED)
def test_ordinary_details_still_work(text):
    from app.directory.lookup import find_company
    c = case(text)
    compose(c, engine.next_action(c, D0, find_company("Swiggy")), D0)
    assert text in build_kit(c, D0).complaint_text


def test_pin_code_of_an_address_is_blocked_on_purpose():
    # Known false positive: "pin code 603203" looks like "pin 603203". We fail closed; the user can write "postal code" instead.
    from app.directory.lookup import find_company
    c = case("pin code 603203")
    with pytest.raises(LetterError):
        compose(c, engine.next_action(c, D0, find_company("Swiggy")), D0)


@pytest.mark.parametrize("text", KNOWN_GAPS)
@pytest.mark.xfail(strict=True, reason="known gap: payment data written in words or split by symbols is not detected yet")
def test_known_gaps_are_not_caught_yet(text):
    from app.directory.lookup import find_company
    c = case(text)
    with pytest.raises(LetterError):
        compose(c, engine.next_action(c, D0, find_company("Swiggy")), D0)
