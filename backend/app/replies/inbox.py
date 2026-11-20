"""Reads the user's Gmail inbox through IMAP in READ-ONLY mode. It cannot delete, move, flag or mark anything read:
the mailbox is opened with readonly=True and every message is fetched with BODY.PEEK."""
import email
import imaplib
import os
import re
from datetime import date
from email.header import decode_header, make_header
from email.utils import parsedate_to_datetime
from typing import Callable

from app.replies.matcher import InboxMessage

_QUOTE = re.compile(r"(\nOn .{0,90}wrote:|\n-{2,}\s*Original Message|\n>)", re.I)


def _text(msg: email.message.Message) -> str:
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            raw = part.get_payload(decode=True) or b""
            return raw.decode(part.get_content_charset() or "utf-8", errors="ignore")
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            raw = (part.get_payload(decode=True) or b"").decode(errors="ignore")
            return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", raw))
    return ""


def parse(raw: bytes) -> InboxMessage:
    msg = email.message_from_bytes(raw)
    body = _text(msg)
    body = _QUOTE.split(body)[0]
    try:
        on = parsedate_to_datetime(msg["Date"]).date()
    except (TypeError, ValueError):
        on = date.today()
    refs = (msg.get("References") or "").split()
    return InboxMessage(message_id=(msg.get("Message-ID") or "").strip() or f"nomid-{hash(raw)}",
                        from_addr=str(make_header(decode_header(msg.get("From", "")))),
                        subject=re.sub(r"\s+", " ", str(make_header(decode_header(msg.get("Subject", ""))))),
                        on=on, snippet=re.sub(r"\s+", " ", body).strip()[:600], in_reply_to=(msg.get("In-Reply-To") or "").strip() or None, references=refs)


class ImapInbox:
    def __init__(self, user: str | None = None, password: str | None = None, host: str = "imap.gmail.com",
                 factory: Callable[[str], imaplib.IMAP4] = imaplib.IMAP4_SSL):
        self.user = user or os.getenv("SMTP_USER", "")
        self.password = password or os.getenv("SMTP_PASSWORD", "")
        self.host, self.factory = host, factory

    def fetch_since(self, since: date, limit: int = 300) -> list[InboxMessage]:
        m = self.factory(self.host)
        out: list[InboxMessage] = []
        try:
            m.login(self.user, self.password)
            m.select("INBOX", readonly=True)                      # read-only: nothing can be changed
            _, data = m.search(None, "SINCE", since.strftime("%d-%b-%Y"))
            for num in data[0].split()[-limit:]:
                _, parts = m.fetch(num, "(BODY.PEEK[])")
                out.append(parse(parts[0][1]))
        finally:
            try:
                m.logout()
            except Exception:  # noqa: BLE001
                pass
        return out
