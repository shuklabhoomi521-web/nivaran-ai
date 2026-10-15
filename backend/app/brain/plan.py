from pydantic import ValidationError

from app.brain.llm import LLMClient, LLMError
from app.models.case import Case, Plan
from app.safety.redact import scrub

SYSTEM_PROMPT = """You plan how to get a customer-care problem solved for an Indian user.
You get a case (JSON). Return a plan.

Rules:
1. channel: "call" for urgent or simple problems where a phone agent can fix it fast (stuck refund,
   cancelled booking, service down). "email" when a written record or attached proof is needed (billing
   disputes, claims, damaged goods). "complaint" for a formal written complaint when the problem is serious,
   high value, or normal support is likely to fail (for example an appeal against a rejected claim).
2. reason: one short sentence in plain English.
3. opening_line: 1-2 polite sentences in English that the assistant will say first about the problem, on
   behalf of the user. Use only facts in details_known. Never invent order ids, dates or amounts. Never
   pretend to be the user: speak as an assistant calling for the user. Do not say the AI disclosure line;
   the system adds that.
4. proof_to_keep: 2-5 short items the user should keep ready (bill, screenshots, photos, order
   confirmation, ...). Never ask for card numbers, CVV, PIN, passwords or OTPs.
"""


def make_plan(case: Case, llm: LLMClient) -> Plan:
    raw = llm.complete_json(
        system=SYSTEM_PROMPT,
        user=case.model_dump_json(),
        schema=Plan.model_json_schema(),
    )
    raw, _ = scrub(raw)
    try:
        return Plan.model_validate(raw)
    except ValidationError as e:
        raise LLMError("The AI answer did not match the plan form.") from e
