import os
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.cases import engine
from app.cases.models import Action, Event, TrackedCase
from app.cases.store import CaseStore
from app.directory.lookup import find_company
from app.models.case import Case

router = APIRouter(prefix="/tracked-cases", tags=["tracked cases"])


def get_store() -> CaseStore:
    return CaseStore(os.getenv("CASE_STORE_FILE", ".cases.json"))


def _today() -> date:
    return date.today()


class CreateRequest(BaseModel):
    case: Case                     # what the AI understood and the user confirmed
    user_name: str | None = None   # signs the letters the user approves


class NextResponse(BaseModel):
    action: Action | None
    reminders: list[dict]


@router.post("", response_model=TrackedCase)
def create(req: CreateRequest, store: CaseStore = Depends(get_store)):
    try:
        case = engine.new_case(req.case, _today(), user_name=req.user_name)
    except engine.CaseError as e:
        raise HTTPException(status_code=422, detail=str(e))
    if find_company(case.company) is None:
        raise HTTPException(status_code=422, detail=f"{case.company} is not in the verified directory yet")
    store.save(case)
    return case


@router.get("", response_model=list[TrackedCase])
def list_cases(store: CaseStore = Depends(get_store)):
    return store.list()


def _get(store: CaseStore, case_id: str) -> TrackedCase:
    case = store.get(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="no such case")
    return case


@router.get("/{case_id}", response_model=TrackedCase)
def get_case(case_id: str, store: CaseStore = Depends(get_store)):
    return _get(store, case_id)


@router.post("/{case_id}/events", response_model=TrackedCase)
def add_event(case_id: str, event: Event, store: CaseStore = Depends(get_store)):
    case = _get(store, case_id)
    try:
        case = engine.apply(case, event)
    except engine.CaseError as e:
        raise HTTPException(status_code=409, detail=str(e))
    store.save(case)
    return case


@router.get("/{case_id}/next", response_model=NextResponse)
def next_step(case_id: str, store: CaseStore = Depends(get_store)):
    case = _get(store, case_id)
    today = _today()
    return NextResponse(action=engine.next_action(case, today, find_company(case.company)), reminders=engine.reminders(case, today))


@router.delete("/{case_id}")
def delete_case(case_id: str, store: CaseStore = Depends(get_store)):
    if not store.delete(case_id):
        raise HTTPException(status_code=404, detail="no such case")
    return {"deleted": case_id}
