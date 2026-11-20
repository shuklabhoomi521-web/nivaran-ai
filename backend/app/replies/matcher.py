"""Reply tracking: match emails in the user's inbox to a tracked case. READ ONLY: nothing is sent, deleted, moved or marked read.
A reply is matched by (1) the Message-ID of a letter we sent, (2) the case reference we put in our letters, or (3) the sender being
a verified directory address or an official company domain. Only a short, redacted snippet is stored, never the whole email."""
import re
from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict

from app.cases.models import Event, EventKind, TrackedCase
from app.directory.models import Company, host_allowed
from app.letters.compose import allowed_recipients
from app.safety.redact import redact


class InboxMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message_id: str
    from_addr: str
    subject: str
    on: date
    snippet: str = ""                 # the first part of the plain text, quotes of older mail removed
    in_reply_to: str | None = None
    references: list[str] = []


class Strength(str, Enum):
    strong = "strong"    # our Message-ID or our case reference is in it
    weak = "weak"        # only the sender looks like the company


class Match(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: InboxMessage
    strength: Strength
    reason: str
    auto_acknowledgement: bool        # a ticket or "we received your message" robot mail, not a human answer
    looks_resolved: bool              # a hint only: the user decides whether it is solved
    docket: str | None


_AUTO = re.compile(r"ticket (has been )?(created|logged|generated)|request (has been )?(received|logged)|we have (successfully )?received|auto[- ]?reply|"
                   r"automatic(ally)? generated|do not reply|out of office|thank you for (contacting|reaching)", re.I)
_RESOLVED = re.compile(r"\b(refund(ed)?|resolved|processed|credited|replacement (has been )?(sent|dispatched)|issue (has been )?fixed|closed your)\b", re.I)
_DOCKET = re.compile(r"(?:ticket|case|reference|docket|complaint|request)\s*(?:id|no\.?|number|#|:)?\s*[:#-]?\s*([A-Z]{0,6}[-_]?\d{4,}[A-Za-z0-9-]*)", re.I)


def _addr(from_header: str) -> str:
    m = re.search(r"<([^>]+)>", from_header)
    return (m.group(1) if m else from_header).strip().lower()


def _domain(addr: str) -> str:
    return addr.rsplit("@", 1)[-1] if "@" in addr else ""


def classify(case: TrackedCase, msg: InboxMessage, company: Company | None, sent_ids: set[str]) -> Match | None:
    text = f"{msg.subject}\n{msg.snippet}"
    addr = _addr(msg.from_addr)
    refs = {x for x in [msg.in_reply_to, *msg.references] if x}
    strength = reason = None
    if refs & sent_ids:
        strength, reason = Strength.strong, "answers a letter we sent (Message-ID)"
    elif re.search(rf"\b{re.escape(case.id)}\b", text):
        strength, reason = Strength.strong, "contains the case reference"
    elif company and (addr in allowed_recipients(company) or host_allowed(_domain(addr), company.official_domains)) and msg.on >= case.created_on:
        strength, reason = Strength.weak, "sent by the company's official address or domain"
    if strength is None:
        return None
    d = _DOCKET.search(text)
    return Match(message=msg, strength=strength, reason=reason, auto_acknowledgement=bool(_AUTO.search(text)),
                 looks_resolved=bool(_RESOLVED.search(msg.snippet)) and not _AUTO.search(text), docket=d.group(1) if d else None)


def sent_message_ids(drafts) -> set[str]:
    return {d.message_id for d in drafts if getattr(d, "message_id", None)}


def track(case: TrackedCase, messages: list[InboxMessage], company: Company | None, sent_ids: set[str], today: date) -> tuple[TrackedCase, list[Match]]:
    """Add one `reply_received` event per new matched message. Returns the updated case and the new matches.
    The case state does not change (a reply is not a solution); `looks_resolved` is only a hint for the user."""
    seen = {e.source_id for e in case.events if e.source_id}
    new: list[Match] = []
    for msg in sorted(messages, key=lambda m: m.on):
        if msg.message_id in seen:
            continue
        match = classify(case, msg, company, sent_ids)
        if match is None:
            continue
        snippet, _ = redact(msg.snippet.strip().replace("\n", " "))
        label = "automatic acknowledgement" if match.auto_acknowledgement else "reply"
        text = f"{label} from {_addr(msg.from_addr)}: {msg.subject[:80]} | {snippet[:240]}"
        if match.strength == Strength.weak:
            text += " (matched by sender only)"
        case = case.model_copy(update={"events": [*case.events, Event(on=max(msg.on, case.created_on), kind=EventKind.reply_received,
                                                                  text=text, docket=match.docket, source_id=msg.message_id)]})
        seen.add(msg.message_id)
        new.append(match)
    return case, new
