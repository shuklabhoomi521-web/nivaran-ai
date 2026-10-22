"""The talking part of the voice page: takes what the user said (text), decides what to say back (text).
Pure logic, no audio: the voice pipeline feeds it transcripts and speaks its replies, so it is easy to test.
Reuses the same brain as the text chat: understand -> ask one question -> contact picker -> plan."""
from dataclasses import dataclass, field

from app.brain.llm import LLMClient
from app.brain.plan import make_plan
from app.brain.speak import FALLBACK, spoken_summary
from app.brain.understand import understand
from app.directory.lookup import find_company
from app.directory.picker import pick_contact, resolve_channel
from app.safety.redact import scrub

LANGUAGE_NAME = {"en-IN": "english", "hi-IN": "hindi", "ta-IN": "tamil", "hinglish": "hinglish"}
GREETING = {
    "en-IN": "Hello, I am Nivaran. Tell me your problem, and which company it is about.",
    "hi-IN": "नमस्ते, मैं निवारण हूँ। अपनी समस्या बताइए, और किस कंपनी के बारे में है।",
    "ta-IN": "வணக்கம், நான் நிவாரண். உங்கள் பிரச்சனையையும், எந்த நிறுவனம் என்பதையும் சொல்லுங்கள்.",
    "hinglish": "Namaste, main Nivaran hoon. Apni problem batayein, aur kis company ke baare mein hai.",
}
MAX_QUESTIONS = 4        # after this many questions we stop asking and summarise what we have


@dataclass
class Turn:
    user: str
    reply: str
    note: str = ""       # a short line for the page's log: what we understood


@dataclass
class Conversation:
    language: str
    llm: LLMClient
    texts: list[str] = field(default_factory=list)
    questions_asked: int = 0
    finished: bool = False
    turns: list[Turn] = field(default_factory=list)

    @property
    def lang_name(self) -> str:
        return LANGUAGE_NAME.get(self.language, "english")

    def greeting(self) -> str:
        return GREETING.get(self.language, GREETING["en-IN"])

    def handle(self, said: str) -> Turn:
        """What the user said -> what we say back."""
        said = said.strip()
        if self.finished:
            return Turn(said, FALLBACK[self.lang_name], "already finished")
        self.texts.append(said)
        result = understand("\n".join(self.texts), self.llm)          # card numbers etc. are removed in here
        case = result.case
        note = f"company={case.company}, category={case.category.value}, goal={case.user_goal.value}"
        if result.redacted:
            note += f" (private data removed: {', '.join(result.redacted)})"
        needs_more = bool(result.follow_up_question) and self.questions_asked < MAX_QUESTIONS
        if needs_more:
            self.questions_asked += 1
            return self._remember(Turn(said, self._clean(result.follow_up_question), note))
        # enough information: contact picker + plan, then a short spoken confirmation
        company = find_company(case.company)
        choice = pick_contact(company) if company else None
        plan_dict: dict = {"can_proceed": False, "note": "company not in the verified directory" if case.company else "company unknown"}
        if choice and choice.channels_available and case.company:
            plan = make_plan(case, self.llm, available_channels=choice.channels_available, no_phone_line=bool(choice.no_phone_notice))
            channel, why = resolve_channel(plan.channel, choice)
            plan_dict = {"channel": channel.value if channel else None, "can_proceed": channel is not None, "note": why}
            note += f"; channel={plan_dict['channel']}"
        self.finished = True
        reply = spoken_summary(case.model_dump(mode="json"), plan_dict, self.lang_name, self.llm)
        return self._remember(Turn(said, self._clean(reply), note))

    def _remember(self, t: Turn) -> Turn:
        self.turns.append(t)
        return t

    @staticmethod
    def _clean(text: str) -> str:
        clean, _ = scrub({"t": text})          # nothing sensitive is ever spoken back
        return clean["t"]
