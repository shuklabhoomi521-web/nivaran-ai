import os
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.tracked import _today, get_store
from app.cases import engine
from app.cases.models import Event, EventKind, TrackedCase
from app.cases.store import CaseStore
from app.directory.lookup import find_company
from app.letters import compose as composer
from app.letters import outbox
from app.letters.compose import LetterError
from app.letters.outbox import Draft, DraftStore, MailSender, SmtpSender

router = APIRouter(tags=["letters"])


def get_drafts() -> DraftStore:
    return DraftStore(os.getenv("DRAFT_STORE_FILE", ".drafts.json"))


def get_sender() -> MailSender:
    try:
        return SmtpSender()
    except LetterError as e:
        raise HTTPException(status_code=500, detail=str(e))


class EditRequest(BaseModel):
    subject: str | None = None
    body: str | None = None


class SendResponse(BaseModel):
    draft: Draft
    case: TrackedCase


def _case(store: CaseStore, case_id: str) -> TrackedCase:
    case = store.get(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="no such case")
    return case


def _draft(drafts: DraftStore, draft_id: str) -> Draft:
    d = drafts.get(draft_id)
    if d is None:
        raise HTTPException(status_code=404, detail="no such draft")
    return d


@router.post("/tracked-cases/{case_id}/drafts", response_model=Draft)
def make_draft(case_id: str, store: CaseStore = Depends(get_store), drafts: DraftStore = Depends(get_drafts)):
    case = _case(store, case_id)
    company = find_company(case.company)
    action = engine.next_action(case, _today(), company)
    if action is None:
        raise HTTPException(status_code=409, detail="nothing left to send on this case")
    try:
        letter = composer.compose(case, action, _today())
    except LetterError as e:
        raise HTTPException(status_code=422, detail=str(e))
    d = outbox.new_draft(case.id, letter, _today())
    drafts.save(d)
    return d


@router.get("/tracked-cases/{case_id}/drafts", response_model=list[Draft])
def list_drafts(case_id: str, drafts: DraftStore = Depends(get_drafts)):
    return drafts.for_case(case_id)


def _change(drafts: DraftStore, draft_id: str, fn) -> Draft:
    d = _draft(drafts, draft_id)
    try:
        d = fn(d)
    except LetterError as e:
        raise HTTPException(status_code=409, detail=str(e))
    drafts.save(d)
    return d


@router.patch("/drafts/{draft_id}", response_model=Draft)
def edit_draft(draft_id: str, req: EditRequest, drafts: DraftStore = Depends(get_drafts)):
    return _change(drafts, draft_id, lambda d: outbox.edit(d, req.subject, req.body))


@router.post("/drafts/{draft_id}/approve", response_model=Draft)
def approve_draft(draft_id: str, drafts: DraftStore = Depends(get_drafts)):
    """The user's explicit yes to exactly this text."""
    return _change(drafts, draft_id, lambda d: outbox.approve(d, _today()))


@router.post("/drafts/{draft_id}/reject", response_model=Draft)
def reject_draft(draft_id: str, drafts: DraftStore = Depends(get_drafts)):
    return _change(drafts, draft_id, outbox.reject)


@router.post("/drafts/{draft_id}/send", response_model=SendResponse)
def send_draft(draft_id: str, store: CaseStore = Depends(get_store), drafts: DraftStore = Depends(get_drafts),
               sender: MailSender = Depends(get_sender)):
    d = _draft(drafts, draft_id)
    case = _case(store, d.case_id)
    try:
        sent = outbox.send(d, find_company(case.company), sender, _today())
        case = engine.apply(case, Event(on=_today(), kind=EventKind.contacted, rung=d.rung, channel="email", text=f"email sent: {d.subject}"))
    except (LetterError, engine.CaseError) as e:
        raise HTTPException(status_code=409, detail=str(e))
    drafts.save(sent)
    store.save(case)
    return SendResponse(draft=sent, case=case)
