from pydantic import ValidationError

from app.brain.llm import LLMClient, LLMError
from app.models.case import Case, UnderstandOutput, UnderstandResponse
from app.safety.redact import redact, scrub

SYSTEM_PROMPT = """You are the intake brain of Nivaran, an app that handles customer care for Indian users.
The user describes a problem with a company, in any language (English, Hindi, Tamil, Hinglish, ...).
Turn it into a clean case. Fill every field of the form.

Rules:
1. company: the brand name in English letters (for example Swiggy, IndiGo, Airtel). Use null if the user did
   not clearly name a company, or only hinted at one (for example "the orange food app"). Never guess a
   company from hints.
2. category: pick the closest one from the allowed list. Use "other" only if none fits.
3. user_goal: what the user wants: refund, repair, replace, cancel, info, or other
   (use "other" for things like a complaint about behaviour or an appeal).
4. problem_summary: one or two plain English sentences.
5. details_known: only facts the user literally wrote (order id, PNR, amount, date, phone number, product,
   claim number, consumer number, ...). Copy each value EXACTLY as the user typed it: same characters, same
   script, no translating, no reformatting. If a fact is not in the message, do not add it. Never put a
   card number, CVV, PIN, password or OTP here. The text may contain markers like [CARD NUMBER REMOVED]:
   ignore them.
6. details_missing: things a company agent would need that the user did not give (short English names like
   order_id, pnr, ride_date, what_happened, product_model). Only what is really needed. At most 3.
   Leave it empty if nothing important is missing. NEVER invent a value for a missing detail.
7. follow_up_question: if details_missing is not empty OR company is null, write ONE short question, in the
   user's own language and script, asking for the single most important missing thing. If the company is
   null, ask for the company name first. Otherwise null. Never ask for a card number, CVV, PIN,
   password or OTP.
8. If the message holds more than one problem, the case is about the main one (the one the user calls
   main, otherwise the first one). Put the other problems in other_issues as short English phrases.
   If there is only one problem, other_issues is an empty list.
9. user_language: the language the user wrote in. Hindi written in English letters is "hinglish".
10. urgency: high if money is stuck, travel is at risk or the user is stranded; low for simple questions;
    otherwise medium.
"""


def understand(message: str, llm: LLMClient) -> UnderstandResponse:
    clean_message, removed = redact(message)  # the AI never sees card numbers, CVVs or PINs
    raw = llm.complete_json(
        system=SYSTEM_PROMPT,
        user=clean_message,
        schema=UnderstandOutput.model_json_schema(),
    )
    raw, removed_again = scrub(raw)  # belt and braces: clean the AI's answer too
    for kind in removed_again:
        if kind not in removed:
            removed.append(kind)
    try:
        output = UnderstandOutput.model_validate(raw)
    except ValidationError as e:
        raise LLMError("The AI answer did not match the case form.") from e
    case = Case.model_validate(output.model_dump(exclude={"follow_up_question"}))
    return UnderstandResponse(case=case, follow_up_question=output.follow_up_question, redacted=removed)
