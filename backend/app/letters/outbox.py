"""Drafts, approval and sending. Rules: nothing is sent without the user's approval; changing a draft after approval cancels the approval;
the recipient must be in the verified directory; payment data is blocked again at send time."""
import hashlib
import json
import os
import smtplib
import ssl
import uuid
from datetime import date
from enum import Enum
from email.message import EmailMessage
from pathlib import Path
from typing import Callable, Protocol

from pydantic import BaseModel, ConfigDict

from app.cases.models import Rung
from app.directory.models import Company
from app.letters.compose import Letter, LetterError, allowed_recipients
from app.safety.redact import redact


class DraftStatus(str, Enum):
    pending = "pending"      # waiting for the user to read it
    approved = "approved"    # the user said yes to exactly this text
    sent = "sent"
    rejected = "rejected"


class Draft(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    case_id: str
    rung: Rung
    channel: str
    to: str
    subject: str
    body: str
    status: DraftStatus = DraftStatus.pending
    created_on: date
    approved_on: date | None = None
    approved_hash: str | None = None
    sent_on: date | None = None
    message_id: str | None = None


def text_hash(subject: str, body: str, to: str) -> str:
    return hashlib.sha256(f"{to}\n{subject}\n{body}".encode()).hexdigest()


class MailSender(Protocol):
    def send(self, to: str, subject: str, body: str) -> str: ...


class SmtpSender:
    """Gmail (or any SMTP) with an app password from the environment. `factory` lets tests use a fake server."""

    def __init__(self, host: str | None = None, port: int | None = None, user: str | None = None, password: str | None = None,
                 from_name: str | None = None, factory: Callable[..., smtplib.SMTP] = smtplib.SMTP):
        self.host = host or os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.port = port or int(os.getenv("SMTP_PORT", "587"))
        self.user = user or os.getenv("SMTP_USER", "")
        self.password = password or os.getenv("SMTP_PASSWORD", "")
        self.from_name = from_name or os.getenv("SENDER_NAME", "")
        self.factory = factory
        if not (self.user and self.password):
            raise LetterError("email sending is not set up: add SMTP_USER and SMTP_PASSWORD to .env")

    def send(self, to: str, subject: str, body: str) -> str:
        msg = EmailMessage()
        msg["From"] = f"{self.from_name} <{self.user}>" if self.from_name else self.user
        msg["To"], msg["Subject"] = to, subject
        msg["Message-ID"] = f"<{uuid.uuid4().hex}@nivaran.local>"
        msg.set_content(body)
        s = self.factory(self.host, self.port, timeout=30)
        try:
            s.starttls(context=ssl.create_default_context())
            s.login(self.user, self.password)
            s.send_message(msg)
        finally:
            s.quit()
        return msg["Message-ID"]


class DraftStore:
    def __init__(self, path: str | os.PathLike):
        self.path = Path(path)

    def _read(self) -> dict[str, dict]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {}

    def save(self, d: Draft) -> None:
        data = self._read()
        data[d.id] = json.loads(d.model_dump_json())
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, self.path)

    def get(self, draft_id: str) -> Draft | None:
        raw = self._read().get(draft_id)
        return Draft.model_validate(raw) if raw else None

    def for_case(self, case_id: str) -> list[Draft]:
        return sorted((Draft.model_validate(v) for v in self._read().values() if v["case_id"] == case_id), key=lambda d: (d.created_on, d.id))


def new_draft(case_id: str, letter: Letter, today: date) -> Draft:
    return Draft(id=uuid.uuid4().hex[:12], case_id=case_id, rung=letter.rung, channel=letter.channel, to=letter.to,
                 subject=letter.subject, body=letter.body, created_on=today)


def edit(d: Draft, subject: str | None, body: str | None) -> Draft:
    if d.status != DraftStatus.pending:
        raise LetterError(f"a {d.status.value} draft cannot be edited; reject it and write a new one")
    return d.model_copy(update={"subject": subject if subject is not None else d.subject, "body": body if body is not None else d.body})


def approve(d: Draft, today: date) -> Draft:
    if d.status != DraftStatus.pending:
        raise LetterError(f"only a pending draft can be approved (this one is {d.status.value})")
    return d.model_copy(update={"status": DraftStatus.approved, "approved_on": today, "approved_hash": text_hash(d.subject, d.body, d.to)})


def reject(d: Draft) -> Draft:
    if d.status in (DraftStatus.sent, DraftStatus.rejected):
        raise LetterError(f"a {d.status.value} draft cannot be rejected")
    return d.model_copy(update={"status": DraftStatus.rejected})


def send(d: Draft, company: Company | None, sender: MailSender, today: date) -> Draft:
    """Send an approved email. Every check runs again here, so a wrong state or text cannot slip through."""
    if d.channel != "email":
        raise LetterError("only email drafts can be sent by the app; portal complaints are filed by the user")
    if d.status != DraftStatus.approved:
        raise LetterError("the user has not approved this draft")
    if d.approved_hash != text_hash(d.subject, d.body, d.to):
        raise LetterError("the text changed after approval; approve it again")
    if d.to.lower() not in allowed_recipients(company):
        raise LetterError(f"{d.to} is not an address in the verified directory for this company")
    if redact(d.subject + "\n" + d.body)[1]:
        raise LetterError("the letter contains payment data (card, CVV or PIN) and was not sent")
    message_id = sender.send(d.to, d.subject, d.body)
    return d.model_copy(update={"status": DraftStatus.sent, "sent_on": today, "message_id": message_id})
