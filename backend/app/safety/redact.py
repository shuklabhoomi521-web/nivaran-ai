"""Safety guard, first version: strip card numbers, CVV and PINs from text.

This runs BEFORE any text goes to the AI, and again on the AI's answer.
Phase 7 builds the full guard. Known limits of this version: it only knows
ASCII digits and English keywords (cvv, pin).
"""
import re
from typing import Any

CARD_PLACEHOLDER = "[CARD NUMBER REMOVED]"
CVV_PLACEHOLDER = "[CVV REMOVED]"
PIN_PLACEHOLDER = "[PIN REMOVED]"

# 13-19 digits, optionally split by single spaces or dashes. Not glued to letters/digits.
_DIGIT_RUN = re.compile(r"(?<![A-Za-z0-9])\d(?:[ -]?\d){12,18}(?![A-Za-z0-9])")
# Usual card layouts: 4-4-4-4(-3), Amex 4-6-5.
_CARD_LAYOUT = re.compile(r"\d{4}([ -])\d{4}\1\d{4}\1\d{1,7}|\d{4}([ -])\d{6}\2\d{5}")
_CVV = re.compile(r"(?i)\b(cvv2?|cvc)\b(\D{0,12})\d{3,4}\b")
_PIN = re.compile(r"(?i)\b(upi\s*pin|atm\s*pin|pin)\b(\D{0,12})\d{4,6}\b")


def luhn_ok(digits: str) -> bool:
    total = 0
    for i, ch in enumerate(reversed(digits)):
        n = int(ch)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def _is_card(match_text: str) -> bool:
    digits = re.sub(r"\D", "", match_text)
    if not 13 <= len(digits) <= 19:
        return False
    return luhn_ok(digits) or bool(_CARD_LAYOUT.fullmatch(match_text))


def redact(text: str) -> tuple[str, list[str]]:
    """Return (clean_text, kinds_removed)."""
    found: list[str] = []

    def card(m: re.Match) -> str:
        if _is_card(m.group(0)):
            if "card_number" not in found:
                found.append("card_number")
            return CARD_PLACEHOLDER
        return m.group(0)

    text = _DIGIT_RUN.sub(card, text)

    def cvv(m: re.Match) -> str:
        if "cvv" not in found:
            found.append("cvv")
        return f"{m.group(1)}{m.group(2)}{CVV_PLACEHOLDER}"

    def pin(m: re.Match) -> str:
        if "pin" not in found:
            found.append("pin")
        return f"{m.group(1)}{m.group(2)}{PIN_PLACEHOLDER}"

    text = _CVV.sub(cvv, text)
    text = _PIN.sub(pin, text)
    return text, found


def scrub(obj: Any) -> tuple[Any, list[str]]:
    """Redact every string inside a nested dict/list (used on the AI's answer)."""
    found: list[str] = []

    def walk(x: Any) -> Any:
        if isinstance(x, str):
            clean, kinds = redact(x)
            for k in kinds:
                if k not in found:
                    found.append(k)
            return clean
        if isinstance(x, list):
            return [walk(i) for i in x]
        if isinstance(x, dict):
            return {k: walk(v) for k, v in x.items()}
        return x

    return walk(obj), found
