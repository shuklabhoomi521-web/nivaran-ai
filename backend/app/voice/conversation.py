"""The talking part of the voice page: takes what the user said (text), decides what to say back (text).
Pure logic, no audio: the voice pipeline feeds it transcripts and speaks its replies, so it is easy to test.
Reuses the same brain as the text chat: understand -> ask one question -> contact picker -> plan."""
from dataclasses import dataclass, field

from app.brain.llm import LLMClient
from app.models.case import Channel
from app.brain.speak import FALLBACK
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
    "auto": "Hello, I am Nivaran. Namaste. Tell me your problem in English, Hindi, Tamil or Hinglish, and which company it is about.",
}
FILLER = {"en-IN": "One moment, please.", "hi-IN": "एक मिनट, कृपया।", "ta-IN": "ஒரு நிமிடம், தயவுசெய்து.", "hinglish": "Ek minute, please."}
APOLOGY = {
    "en-IN": "Sorry, I could not get that. Please say it again.",
    "hi-IN": "माफ़ कीजिए, मैं समझ नहीं पाया। कृपया दोबारा बोलिए।",
    "ta-IN": "மன்னிக்கவும், எனக்குப் புரியவில்லை. தயவுசெய்து மீண்டும் சொல்லுங்கள்.",
    "hinglish": "Sorry, main samajh nahi paya. Please dobara boliye.",
}
# Second sentence of the final answer: made by us (not the AI), so it is always right about what was and was not done.
HOW = {
    "en-IN": {"call": "I can call {c} for you. Nothing has been done yet.",
              "email": "I can email {c} for you, once you approve it. Nothing has been sent yet.",
              "complaint": "I can file a formal complaint with {c}. Nothing has been sent yet.",
              None: "I cannot reach this company yet. Nothing has been sent."},
    "hi-IN": {"call": "मैं आपके लिए {c} को कॉल कर सकता हूँ। अभी कुछ किया नहीं गया है।",
              "email": "आपकी मंज़ूरी के बाद मैं {c} को ईमेल कर सकता हूँ। अभी कुछ भेजा नहीं गया है।",
              "complaint": "मैं {c} के पास औपचारिक शिकायत दर्ज कर सकता हूँ। अभी कुछ भेजा नहीं गया है।",
              None: "मैं अभी इस कंपनी तक नहीं पहुँच सकता। कुछ भेजा नहीं गया है।"},
    "ta-IN": {"call": "நான் உங்களுக்காக {c} நிறுவனத்தை அழைக்க முடியும். இன்னும் எதுவும் செய்யப்படவில்லை.",
              "email": "உங்கள் ஒப்புதலுக்குப் பிறகு {c} நிறுவனத்திற்கு மின்னஞ்சல் அனுப்ப முடியும். இன்னும் எதுவும் அனுப்பப்படவில்லை.",
              "complaint": "{c} நிறுவனத்திடம் முறையான புகார் பதிவு செய்ய முடியும். இன்னும் எதுவும் அனுப்பப்படவில்லை.",
              None: "இந்த நிறுவனத்தை இன்னும் என்னால் தொடர்பு கொள்ள முடியவில்லை. எதுவும் அனுப்பப்படவில்லை."},
    "hinglish": {"call": "Main aapke liye {c} ko call kar sakta hoon. Abhi kuch kiya nahi gaya hai.",
                 "email": "Aapki manzoori ke baad main {c} ko email kar sakta hoon. Abhi kuch bheja nahi gaya hai.",
                 "complaint": "Main {c} ke paas formal complaint kar sakta hoon. Abhi kuch bheja nahi gaya hai.",
                 None: "Main abhi is company tak nahi pahunch sakta. Kuch bheja nahi gaya hai."},
}
MAX_QUESTIONS = 4        # after this many questions we stop asking and summarise what we have


@dataclass
class Turn:
    user: str
    reply: str
    note: str = ""       # a short line for the page's log: what we understood
    language: str = ""   # the language this reply is in (it follows the user, who may switch)


@dataclass
class Conversation:
    language: str
    llm: LLMClient
    texts: list[str] = field(default_factory=list)
    questions_asked: int = 0
    finished: bool = False
    turns: list[Turn] = field(default_factory=list)
    _epoch: int = 0

    @property
    def lang_name(self) -> str:
        return LANGUAGE_NAME.get(self.language, "english")

    def snapshot(self) -> tuple:
        return (list(self.texts), self.questions_asked, self.finished, len(self.turns), self.language)

    def restore(self, snap: tuple) -> None:
        """Go back to how things were before a turn (used when the user kept talking while we were still thinking)."""
        self.texts, self.questions_asked, self.finished, self.language = list(snap[0]), snap[1], snap[2], snap[4]
        del self.turns[snap[3]:]
        self._epoch += 1

    def greeting(self) -> str:
        return GREETING.get(self.language, GREETING["en-IN"])

    def handle(self, said: str) -> Turn:
        """What the user said -> what we say back. ONE AI call. Changes the conversation only if nobody
        rewound it meanwhile (a slow answer that arrives after we gave up must not change anything)."""
        said = said.strip()
        epoch = self._epoch
        if self.finished:
            return Turn(said, FALLBACK[self.lang_name], "already finished", self.language)
        texts = self.texts + [said]
        # the AI sees the earlier messages and, clearly marked, the LAST one: the reply must be in the language of the last one
        message = said if len(texts) == 1 else "Earlier messages:\n" + "\n".join(texts[:-1]) + "\n\nLAST MESSAGE (answer in its language): " + said
        result = understand(message, self.llm, from_speech=True)     # card numbers etc. are removed in here (strictly: it is speech)
        case = result.case
        lang = result.reply_language if result.reply_language in HOW else self.language    # the user may have switched language
        note = f"company={case.company}, category={case.category.value}, goal={case.user_goal.value}"
        if result.redacted:
            note += f" (private data removed: {', '.join(result.redacted)})"
        needs_more = bool(result.follow_up_question) and self.questions_asked < MAX_QUESTIONS
        if needs_more:
            turn = Turn(said, self._clean(result.follow_up_question), note, lang)
            return self._commit(epoch, texts, turn, asked=True)
        # enough information: contact picker, then the spoken confirmation (AI's sentence + our sentence)
        company = find_company(case.company)
        choice = pick_contact(company) if company else None
        channel = None
        if choice and choice.channels_available and case.company:
            channel, _why = resolve_channel(Channel.call, choice)
            note += f"; channel={channel.value if channel else None}"
        first = (result.spoken_reply or "").strip() or FALLBACK[self.lang_name]
        how = HOW.get(lang, HOW["en-IN"])[channel.value if channel else None].format(c=case.company or "")
        turn = Turn(said, self._clean(f"{first} {how}"), note, lang)
        return self._commit(epoch, texts, turn, finished=True)

    def _commit(self, epoch: int, texts: list[str], turn: Turn, asked: bool = False, finished: bool = False) -> Turn:
        if epoch != self._epoch:
            return turn                       # we were rewound: this answer is stale, change nothing
        self.texts = texts
        self.language = turn.language or self.language      # the language follows the user
        self.questions_asked += int(asked)
        self.finished = self.finished or finished
        self.turns.append(turn)
        return turn

    @staticmethod
    def _clean(text: str) -> str:
        clean, _ = scrub({"t": text})          # nothing sensitive is ever spoken back
        return clean["t"]
