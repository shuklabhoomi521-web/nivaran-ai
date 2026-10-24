"""The AI on a PHONE CALL to a company: it speaks for the user. Pure logic (text in, text out), so it is easy to test.

Hard rules, enforced in code and not only in the prompt:
- the very first thing said is always "I am an AI assistant calling on behalf of a customer" (fixed text, never written by the AI);
- it only uses facts the user gave us (details_known); it never invents an order number or says it is the customer;
- it never says or accepts a card number, CVV, PIN, password or OTP: if the agent asks for one, it refuses in fixed words;
- the user can stop the call at any time (hang up is handled by the call layer, outside this file)."""
import re
from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.brain.llm import LLMClient, LLMError
from app.safety.redact import scrub


class CallTurnOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    say: str                                   # what to say next (first field: it can be spoken as soon as it is written)
    action: Literal["continue", "press_digits", "wait", "need_user", "end_call"]
    digits: str                                # keypad digits to press when action is press_digits, otherwise an empty string


DISCLOSURE = {
    "en-IN": "Hello. I am an AI assistant calling on behalf of a customer about {company}. May I explain the problem?",
    "hi-IN": "नमस्ते। मैं एक AI असिस्टेंट हूँ और एक ग्राहक की ओर से {company} के बारे में कॉल कर रहा हूँ। क्या मैं समस्या बता सकता हूँ?",
    "ta-IN": "வணக்கம். நான் ஒரு AI உதவியாளர். ஒரு வாடிக்கையாளர் சார்பாக {company} பற்றி அழைக்கிறேன். பிரச்சனையை விளக்கலாமா?",
    "hinglish": "Namaste. Main ek AI assistant hoon aur ek customer ki taraf se {company} ke baare mein call kar raha hoon. Kya main problem bata sakta hoon?",
}
REFUSE_SECRET = {
    "en-IN": "I am sorry, I cannot share or accept card numbers, PINs, passwords or one-time codes on a call. The customer will handle that themselves.",
    "hi-IN": "माफ़ कीजिए, मैं कॉल पर कार्ड नंबर, पिन, पासवर्ड या OTP न बता सकता हूँ, न ले सकता हूँ। ग्राहक यह खुद करेंगे।",
    "ta-IN": "மன்னிக்கவும், அழைப்பில் கார்டு எண், பின், கடவுச்சொல் அல்லது OTP ஐ என்னால் பகிரவோ பெறவோ முடியாது. வாடிக்கையாளர் அதைத் தாமே செய்வார்.",
    "hinglish": "Maaf kijiye, main call par card number, PIN, password ya OTP na de sakta hoon, na le sakta hoon. Customer yeh khud karenge.",
}
NEED_USER = {
    "en-IN": "I do not have that information. Let me check with the customer and get back to you.",
    "hi-IN": "मेरे पास यह जानकारी नहीं है। मैं ग्राहक से पूछकर बताता हूँ।",
    "ta-IN": "என்னிடம் அந்தத் தகவல் இல்லை. வாடிக்கையாளரிடம் கேட்டு சொல்கிறேன்.",
    "hinglish": "Mere paas yeh jaankari nahi hai. Main customer se poochkar batata hoon.",
}
GOODBYE = {"en-IN": "Thank you for your help. Goodbye.", "hi-IN": "आपकी मदद के लिए धन्यवाद। नमस्ते।",
           "ta-IN": "உங்கள் உதவிக்கு நன்றி. வணக்கம்.", "hinglish": "Aapki madad ke liye shukriya. Namaste."}
HOLD_TEXT = {"en-IN": "Yes, I am still here.", "hi-IN": "जी, मैं यहीं हूँ।", "ta-IN": "ஆம், நான் இங்கே இருக்கிறேன்.", "hinglish": "Ji, main yahin hoon."}

# the agent is asking for something we must never give: card number, CVV, PIN, password, OTP / one time code
_SECRET_ASK = re.compile(
    r"(\botp\b|one[- ]?time (pass(word|code)|code)|\bcvv\b|\bpin\b|card number|credit card|debit card|password|passcode|"
    r"ओटीपी|\bओ\.?टी\.?पी\b|सीवीवी|पिन|कार्ड (का )?नंबर|पासवर्ड|ஓடிபி|ஒன் டைம்|பின் நம்பர்|கார்டு (எண்|நம்பர்)|பாஸ்வேர்ட்)", re.I)

SYSTEM_PROMPT = """You are Nivaran, an AI assistant that phones a company's customer care on behalf of a customer in India.
You have already said that you are an AI assistant calling for a customer. You are NOT the customer; never say you are.
You get: the case (company, problem, what the customer wants, facts the customer gave), the language, the conversation so far,
and what the agent just said. Reply with ONE short spoken turn (one or two short sentences, in the language given; Hindi in Devanagari,
Tamil in Tamil script, hinglish = Hindi in English letters).
Rules:
1. Use only the facts in details_known. Never invent an order number, name, address, phone number or amount. If the agent asks for a fact you do not have, set action need_user.
2. Never give or ask for a card number, CVV, PIN, password or OTP. If the agent asks, politely say the customer will handle it, action continue.
3. State the problem and the wanted outcome plainly and ask for a clear next step (refund, replacement, ticket number, timeline). Ask for a ticket or reference number before the call ends.
4. If a keypad menu is read out ("press 1 for ..."), choose the option that fits the problem and set action press_digits with the digits (for example "1"). Otherwise digits is an empty string.
5. If the agent asks you to hold or wait, say a short thanks and set action wait. If the issue is solved or the agent says goodbye, set action end_call with a short polite goodbye.
6. Be polite and brief. Do not argue. Never promise anything on the customer's behalf (no payments, no cancellations)."""


@dataclass
class CallConversation:
    case: dict                                  # company, problem_summary, user_goal, details_known (list of {name, value})
    language: str = "en-IN"
    llm: LLMClient | None = None
    history: list[tuple[str, str]] = field(default_factory=list)      # ("agent"|"ai", text)
    ended: bool = False
    max_turns: int = 14
    last_action: str = "continue"
    last_digits: str = ""

    @property
    def company(self) -> str:
        return self.case.get("company") or "your company"

    def opening(self) -> str:
        """Always first, always fixed text: the AI says what it is."""
        text = DISCLOSURE.get(self.language, DISCLOSURE["en-IN"]).format(company=self.company)
        self.history.append(("ai", text))
        return text

    def _fixed(self, table: dict, action: str = "continue") -> str:
        text = table.get(self.language, table["en-IN"])
        self.history.append(("ai", text))
        self.last_action, self.last_digits = action, ""
        return text

    def respond(self, agent_said: str) -> str:
        """What the agent said -> what we say. Sets last_action (continue, press_digits, wait, need_user, end_call) and last_digits."""
        agent_said = agent_said.strip()
        self.history.append(("agent", agent_said))
        if len([1 for who, _ in self.history if who == "ai"]) >= self.max_turns:
            self.ended = True
            return self._fixed(GOODBYE, "end_call")
        if _SECRET_ASK.search(agent_said):                       # decided in code, never left to the AI
            return self._fixed(REFUSE_SECRET)
        payload = {"language": self.language, "case": {k: self.case.get(k) for k in ("company", "problem_summary", "user_goal", "details_known")},
                   "conversation": [{"who": w, "text": t} for w, t in self.history[-12:]], "agent_just_said": agent_said}
        import json
        try:
            raw = self.llm.complete_json(system=SYSTEM_PROMPT, user=json.dumps(payload, ensure_ascii=False), schema=CallTurnOutput.model_json_schema())
            out = CallTurnOutput.model_validate(raw)
        except Exception:  # noqa: BLE001 - never go silent on a call
            return self._fixed(NEED_USER, "need_user")
        say = scrub({"t": out.say})[0]["t"].strip()
        if _SECRET_ASK.search(say) and not _is_refusal(say):       # the AI itself must not ask for or offer secrets
            return self._fixed(REFUSE_SECRET)
        if not say:
            return self._fixed(HOLD_TEXT if out.action == "wait" else NEED_USER, out.action if out.action in ("wait", "need_user") else "need_user")
        digits = re.sub(r"[^0-9*#]", "", out.digits) if out.action == "press_digits" else ""
        action = out.action if (out.action != "press_digits" or digits) else "continue"
        self.last_action, self.last_digits = action, digits
        if action == "end_call":
            self.ended = True
        self.history.append(("ai", say))
        return say


def _is_refusal(text: str) -> bool:
    return bool(re.search(r"cannot|can't|not able|unable|never|won't|customer will|नहीं|न |முடியாது|nahi|na ", text, re.I))
