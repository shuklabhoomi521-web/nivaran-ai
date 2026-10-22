"""Turns a finished case into a short spoken confirmation in the user's own language."""
import json

from pydantic import BaseModel, ConfigDict, ValidationError

from app.brain.llm import LLMClient, LLMError
from app.safety.redact import scrub


class SpokenReply(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reply: str


SYSTEM_PROMPT = """You are Nivaran, a voice assistant that helps people with customer-care problems in India.
You get a case (JSON), how we would contact the company, and the user's language.
Write what you will SAY OUT LOUD, at most two short sentences, in the user's language:
- the user's language is one of: english, hindi (write Devanagari), tamil (write Tamil script), hinglish (Hindi in English letters).
- sentence 1: what you understood (company, the problem, what the user wants).
- sentence 2: how you would contact the company (call, email or formal complaint) and that nothing has been sent yet.
Rules: no phone numbers, no email addresses, no order numbers, no card numbers. Never ask for OTP, PIN, CVV or passwords.
If "can_proceed" is false, say you cannot reach this company yet and nothing has been sent. Keep it plain and warm."""

FALLBACK = {
    "english": "I understood your problem. I have not sent anything yet.",
    "hindi": "मैं आपकी समस्या समझ गया। अभी कुछ भेजा नहीं गया है।",
    "tamil": "உங்கள் பிரச்சனையைப் புரிந்துகொண்டேன். இன்னும் எதுவும் அனுப்பப்படவில்லை.",
    "hinglish": "Maine aapki problem samjhi. Abhi kuch bheja nahi gaya hai.",
}


def spoken_summary(case: dict, plan: dict, language: str, llm: LLMClient) -> str:
    payload = {"language": language, "case": case,
               "channel": plan.get("channel"), "can_proceed": plan.get("can_proceed"), "company_note": plan.get("note")}
    try:
        raw = llm.complete_json(system=SYSTEM_PROMPT, user=json.dumps(payload, ensure_ascii=False), schema=SpokenReply.model_json_schema())
        text = SpokenReply.model_validate(raw).reply.strip()
    except (LLMError, ValidationError):
        return FALLBACK.get(language, FALLBACK["english"])
    clean, _ = scrub({"t": text})
    return clean["t"] or FALLBACK.get(language, FALLBACK["english"])
