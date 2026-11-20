"""The letter writer. No AI is used here: every sentence is a fixed template filled only with what the user told us and what happened
on the case. That makes it impossible to invent a fact, a law, a deadline or a promise. The user reads and approves every letter."""
import re
import unicodedata
from datetime import date

from pydantic import BaseModel, ConfigDict

from app.cases.models import Action, EventKind, Rung, TrackedCase
from app.directory.models import Company
from app.models.case import UserGoal
from app.safety.redact import redact

GOAL_TEXT = {UserGoal.refund: "a refund", UserGoal.repair: "a repair", UserGoal.replace: "a replacement",
             UserGoal.cancel: "cancellation", UserGoal.info: "clear information", UserGoal.other: "a resolution"}


class LetterError(ValueError):
    pass


def private_kinds(text: str) -> list[str]:
    """Kinds of payment data in the text (card, CVV, PIN). Digits written in other scripts (Devanagari, Arabic-Indic, full-width) are read as
    ordinary digits first, so a card number cannot hide in them."""
    flat = "".join(str(unicodedata.digit(ch)) if ch.isdigit() and ch not in "0123456789" and unicodedata.digit(ch, None) is not None else ch for ch in text)
    flat = re.sub(r"(?<=\d{4})\.(?=\d{4})", " ", flat)              # 4111.1111.1111.1111 is read as 4111 1111 1111 1111
    return redact(flat)[1]


class Letter(BaseModel):
    model_config = ConfigDict(extra="forbid")
    channel: str                 # "email" or "portal"
    to: str                      # an email address, or the portal link for a complaint the user files by hand
    subject: str
    body: str
    rung: Rung


def allowed_recipients(company: Company | None) -> set[str]:
    """The only email addresses a letter may go to: the ones in the verified directory entry."""
    if company is None:
        return set()
    out = {e.value.lower() for e in company.emails}
    for officer in (company.grievance_officer, company.appellate_authority):
        if officer and officer.email:
            out.add(officer.email.lower())
    return out


def _day(d: date) -> str:
    return f"{d.day} {d.strftime('%B %Y')}"


def _facts(case: TrackedCase) -> str:
    if not case.facts:
        return ""
    lines = "\n".join(f"- {f.name.replace('_', ' ')}: {f.value}" for f in case.facts)
    return f"\nDetails I can confirm:\n{lines}\n"


def _history(case: TrackedCase) -> str:
    contacts = [e for e in case.events if e.kind == EventKind.contacted]
    if not contacts:
        return ""
    lines = "\n".join(f"- {_day(e.on)}: {e.channel or 'contact'}" + (f" ({e.text})" if e.text else "") for e in contacts)
    dockets = [e.docket for e in case.events if e.docket]
    extra = f"\nReference numbers given so far: {', '.join(dockets)}\n" if dockets else ""
    return f"\nWhat I have done so far:\n{lines}\n{extra}"


def _ask(case: TrackedCase) -> str:
    return f"What I am asking for: {GOAL_TEXT[case.user_goal]}."


def compose(case: TrackedCase, action: Action, today: date) -> Letter:
    if not action.target_value:
        raise LetterError("there is no verified contact for this step: nothing to write to")
    name = case.user_name or "A customer"
    ref = f"Case reference: {case.id}"
    sign = f"Regards,\n{name}"
    subject_core = f"{case.company}: {GOAL_TEXT[case.user_goal]} ({case.id})"
    rung = action.rung
    if rung == Rung.first_contact:
        subject = f"Complaint to {subject_core}"
        body = (f"Dear {case.company} Customer Support,\n\nI am writing about this problem: {case.problem_summary}\n{_facts(case)}\n"
                f"{_ask(case)}\nPlease reply in writing and tell me what you will do and by when.\n\n{ref}\n\n{sign}\n")
    elif rung == Rung.follow_up:
        first = next((e.on for e in case.events if e.rung == Rung.first_contact), case.created_on)
        subject = f"Follow-up: {subject_core}"
        body = (f"Dear {case.company} Customer Support,\n\nI wrote to you on {_day(first)} about this problem and have not had a solution: "
                f"{case.problem_summary}\n{_facts(case)}\n{_ask(case)}\nPlease reply in writing.\n\n{ref}\n\n{sign}\n")
    elif rung in (Rung.grievance_officer, Rung.appellate):
        who = "Grievance Officer" if rung == Rung.grievance_officer else "Appellate Authority"
        subject = f"{'Escalation' if rung == Rung.grievance_officer else 'Appeal'}: {subject_core}"
        body = (f"Dear {who}, {case.company},\n\nMy problem is still not solved. {case.problem_summary}\n{_facts(case)}{_history(case)}\n"
                f"{_ask(case)}\nI request that you look into this and reply in writing.\n\n{ref}\n\n{sign}\n")
    else:
        subject = f"Complaint text for {action.target_label}: {subject_core}"
        body = (f"Complaint against {case.company}\n\nProblem: {case.problem_summary}\n{_facts(case)}{_history(case)}\n"
                f"{_ask(case)}\n\n{ref}\nFiled by: {name}\n")
    kinds = private_kinds(body)
    if kinds:
        raise LetterError(f"the letter would contain private payment data ({', '.join(kinds)}); remove it from the case facts first")
    return Letter(channel="email" if action.channel == "email" else "portal", to=action.target_value, subject=subject, body=body, rung=rung)
