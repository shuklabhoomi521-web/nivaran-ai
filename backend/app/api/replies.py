from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.letters import get_drafts
from app.api.tracked import _today, get_store
from app.cases.models import TrackedCase
from app.cases.store import CaseStore
from app.directory.lookup import find_company
from app.letters.outbox import DraftStore
from app.replies import matcher
from app.replies.inbox import ImapInbox
from app.replies.matcher import InboxMessage, Match

router = APIRouter(tags=["replies"])


class Inbox:
    def fetch_since(self, since, limit: int = 300) -> list[InboxMessage]: ...


def get_inbox():
    if not (ImapInbox().user and ImapInbox().password):
        raise HTTPException(status_code=500, detail="inbox access is not set up: add SMTP_USER and SMTP_PASSWORD to .env")
    return ImapInbox()


class CheckResponse(BaseModel):
    new_replies: list[Match]
    case: TrackedCase


@router.post("/tracked-cases/{case_id}/check-replies", response_model=CheckResponse)
def check_replies(case_id: str, store: CaseStore = Depends(get_store), drafts: DraftStore = Depends(get_drafts), inbox=Depends(get_inbox)):
    """Read-only: looks through the inbox for replies to this case and adds them to its timeline. Sends and changes nothing in the mailbox."""
    case = store.get(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="no such case")
    messages = inbox.fetch_since(case.created_on)
    case, new = matcher.track(case, messages, find_company(case.company), matcher.sent_message_ids(drafts.for_case(case.id)), _today())
    if new:
        store.save(case)
    return CheckResponse(new_replies=new, case=case)
