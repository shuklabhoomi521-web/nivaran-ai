import os
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import current_user
from app.cases import consent, engine
from app.cases.kit import PortalKit, build_kit
from app.cases.models import Action, Event, TrackedCase
from app.letters.compose import LetterError
from app.cases.store import CaseStore
from app.directory.lookup import find_company
from app.users import LEGACY_OWNER
from app.models.case import Case

router = APIRouter(prefix="/tracked-cases", tags=["tracked cases"])


def get_store() -> CaseStore:
    return CaseStore(os.getenv("CASE_STORE_FILE", ".cases.json"))


def _today() -> date:
    return date.today()


class CreateRequest(BaseModel):
    case: Case                     # what the AI understood and the user confirmed
    user_name: str | None = None   # signs the letters the user approves
    consent: bool = False          # the user accepted the privacy notice (see GET /tracked-cases/consent-notice)
    adult: bool = False            # the user confirmed they are 18 or older


class NextResponse(BaseModel):
    action: Action | None
    reminders: list[dict]


@router.get("/consent-notice")
def consent_notice():
    return consent.notice()


@router.post("", response_model=TrackedCase)
def create(req: CreateRequest, store: CaseStore = Depends(get_store), user: str = Depends(current_user)):
    if not req.consent:
        raise HTTPException(status_code=422, detail="the user has not accepted the privacy notice")
    if not req.adult:
        raise HTTPException(status_code=422, detail="Nivaran is for people aged 18 or older; a parent or guardian must start the case")
    try:
        case = engine.new_case(req.case, _today(), user_name=req.user_name, consent_version=consent.CONSENT_VERSION, adult_confirmed=True, owner_id=user)
    except engine.CaseError as e:
        raise HTTPException(status_code=422, detail=str(e))
    if find_company(case.company) is None:
        raise HTTPException(status_code=422, detail=f"{case.company} is not in the verified directory yet")
    store.save(case)
    return case


@router.get("", response_model=list[TrackedCase])
def list_cases(store: CaseStore = Depends(get_store), user: str = Depends(current_user)):
    return [c for c in store.list() if (c.owner_id or LEGACY_OWNER) == user]


def _get(store: CaseStore, case_id: str, user: str = LEGACY_OWNER) -> TrackedCase:
    """The case, or 404 if it does not exist OR belongs to someone else (the two look the same on purpose)."""
    case = store.get(case_id)
    if case is None or (case.owner_id or LEGACY_OWNER) != user:
        raise HTTPException(status_code=404, detail="no such case")
    return case


@router.get("/{case_id}", response_model=TrackedCase)
def get_case(case_id: str, store: CaseStore = Depends(get_store), user: str = Depends(current_user)):
    return _get(store, case_id, user)


@router.post("/{case_id}/events", response_model=TrackedCase)
def add_event(case_id: str, event: Event, store: CaseStore = Depends(get_store), user: str = Depends(current_user)):
    case = _get(store, case_id, user)
    try:
        case = engine.apply(case, event)
    except engine.CaseError as e:
        raise HTTPException(status_code=409, detail=str(e))
    store.save(case)
    return case


@router.get("/{case_id}/next", response_model=NextResponse)
def next_step(case_id: str, store: CaseStore = Depends(get_store), user: str = Depends(current_user)):
    case = _get(store, case_id, user)
    today = _today()
    return NextResponse(action=engine.next_action(case, today, find_company(case.company)), reminders=engine.reminders(case, today))


@router.delete("/{case_id}")
def delete_case(case_id: str, store: CaseStore = Depends(get_store), user: str = Depends(current_user)):
    _get(store, case_id, user)                       # 404 unless it is this person's own case
    if not store.delete(case_id):
        raise HTTPException(status_code=404, detail="no such case")
    return {"deleted": case_id}


@router.get("/{case_id}/portal-kit", response_model=PortalKit)
def portal_kit(case_id: str, store: CaseStore = Depends(get_store), user: str = Depends(current_user)):
    """The kit for filing on the regulator's official portal: official steps with quotes, our checklist, and a complaint text to paste."""
    case = _get(store, case_id, user)
    try:
        return build_kit(case, _today())
    except LetterError as e:
        raise HTTPException(status_code=422, detail=str(e))
