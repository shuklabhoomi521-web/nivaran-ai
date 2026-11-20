"""Call for me: the app side of Phase 4's call machinery.

SAFETY (all tested):
- PRACTICE MODE is the default: Nivaran rings the USER'S OWN allow-listed number and the user plays the company. No real company is called.
- Real company calls need REAL_COMPANY_CALLS=true in the environment (off) AND the company number on PHONE_ALLOWED_NUMBERS (the voice server refuses everything else).
- The user must confirm each call. The first words are the fixed AI-disclosure sentence (never written by the AI). Hang up works at any time.
- Spoken text is cleaned of card, CVV and PIN before it is shown in the app."""
import os
from datetime import date

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.tracked import _today, get_store
from app.auth import current_user, is_owner
from app.cases import engine
from app.cases.models import Event, EventKind
from app.cases.store import CaseStore
from app.directory.lookup import find_company
from app.directory.picker import pick_contact
from app.safety.redact import redact
from app.users import LEGACY_OWNER
from app.voice.call_conversation import DISCLOSURE

router = APIRouter(prefix="/tracked-cases", tags=["calls"])
LANGS = tuple(DISCLOSURE)


def get_voice() -> httpx.Client:
    return httpx.Client(base_url=os.getenv("VOICE_SERVER_URL", "http://127.0.0.1:7861"), timeout=20)


def real_calls_enabled() -> bool:
    return os.getenv("REAL_COMPANY_CALLS", "").strip().lower() in ("1", "true", "yes")


def own_number() -> str | None:
    nums = [n.strip() for n in os.getenv("PHONE_ALLOWED_NUMBERS", "").split(",") if n.strip()]
    return nums[0] if len(nums) == 1 else None


def mask(number: str | None) -> str | None:
    if not number:
        return None
    digits = "".join(ch for ch in number if ch.isdigit())
    return ("+" if number.strip().startswith("+") else "") + "•" * max(len(digits) - 3, 0) + digits[-3:]


class CallPreview(BaseModel):
    company: str
    language: str
    disclosure: str                     # the exact first sentence the AI will say
    facts: list[str]                    # the only facts the AI may use: what the user gave
    mode: str                           # "practice" or "real"
    will_ring: str | None               # masked number
    company_number: str | None          # from the verified directory, shown for information
    company_number_source: str | None
    can_start: bool
    why_not: str | None
    rules: list[str]


class StartRequest(BaseModel):
    language: str = "en-IN"
    confirm: bool = False


class StartResponse(BaseModel):
    call_id: str
    mode: str


def _case(store: CaseStore, case_id: str, user: str = LEGACY_OWNER):
    c = store.get(case_id)
    if c is None or (c.owner_id or LEGACY_OWNER) != user:
        raise HTTPException(status_code=404, detail="no such case")
    return c


def _owner_only(user: str) -> None:
    if not is_owner(user):
        raise HTTPException(status_code=403, detail="calls are only available to the pilot owner: they ring the owner's phone")


def _check_lang(language: str) -> None:
    if language not in LANGS:
        raise HTTPException(status_code=422, detail=f"language must be one of {', '.join(LANGS)}")


def _target(case):
    company = find_company(case.company)
    choice = pick_contact(company) if company else None
    return choice.phone if choice else None


@router.get("/{case_id}/call/preview", response_model=CallPreview)
def preview(case_id: str, language: str = "en-IN", store: CaseStore = Depends(get_store), user: str = Depends(current_user)):
    case = _case(store, case_id, user)
    _check_lang(language)
    phone = _target(case)
    mode = "real" if real_calls_enabled() else "practice"
    ring = (phone.value if (mode == "real" and phone) else own_number())
    why = None
    if not is_owner(user):
        why = "Calls are only available to the pilot owner, because they ring the owner's phone."
    elif not case.is_open:
        why = "This case is closed."
    elif mode == "practice" and own_number() is None:
        why = "Practice calls ring your own phone. Put exactly one number (yours) in PHONE_ALLOWED_NUMBERS in .env first."
    elif mode == "real" and phone is None:
        why = "No verified phone number for this company."
    rules = ["The first thing said is a fixed sentence: it is an AI assistant calling for a customer.",
             "It never gives or takes a card number, PIN, CVV, password or one-time code.",
             "It only uses the facts shown here. It is never the customer.",
             "You can hang up at any moment."]
    if mode == "practice":
        rules.insert(0, "PRACTICE CALL: Nivaran rings YOUR phone and you play the company. No real company is called.")
    return CallPreview(company=case.company, language=language, disclosure=DISCLOSURE[language].format(company=case.company),
                       facts=[f"{f.name.replace('_', ' ')}: {f.value}" for f in case.facts] + [f"Problem: {case.problem_summary}"],
                       mode=mode, will_ring=mask(ring), company_number=phone.value if phone else None,
                       company_number_source=phone.source_url if phone else None, can_start=why is None, why_not=why, rules=rules)


@router.post("/{case_id}/call", response_model=StartResponse)
def start(case_id: str, req: StartRequest, store: CaseStore = Depends(get_store), voice: httpx.Client = Depends(get_voice), user: str = Depends(current_user)):
    case = _case(store, case_id, user)
    _owner_only(user)
    _check_lang(req.language)
    if not req.confirm:
        raise HTTPException(status_code=422, detail="the user has not confirmed this call")
    if not case.is_open:
        raise HTTPException(status_code=409, detail="this case is closed")
    phone = _target(case)
    mode = "real" if real_calls_enabled() else "practice"
    number = phone.value if (mode == "real" and phone) else own_number()
    if not number:
        raise HTTPException(status_code=409, detail="no number to ring: set PHONE_ALLOWED_NUMBERS (your own number) in .env" if mode == "practice" else "no verified phone number for this company")
    payload = {"to_number": number, "language": req.language, "confirm": True,
               "case": {"company": case.company, "problem_summary": case.problem_summary, "user_goal": case.user_goal.value,
                        "details_known": [f.model_dump() for f in case.facts]}}
    try:
        r = voice.post("/phone/call", json=payload)
    except httpx.HTTPError:
        raise HTTPException(status_code=503, detail="the voice server is not running: start it with scripts/phone_session.py start (it needs a network that can carry the tunnel)")
    if r.status_code != 200:
        raise HTTPException(status_code=502 if r.status_code >= 500 else 409, detail=f"the call was not placed: {r.json().get('detail', r.text[:160]) if r.headers.get('content-type', '').startswith('application/json') else r.text[:160]}")
    note = "practice call started: Nivaran rang the user's own phone, no company was called" if mode == "practice" else "call started to the company's verified number"
    try:
        store.save(engine.apply(case, Event(on=_today(), kind=EventKind.note, text=note)))
    except engine.CaseError:
        pass
    return StartResponse(call_id=r.json()["call_id"], mode=mode)


@router.post("/{case_id}/call/{call_id}/hangup")
def hang_up(case_id: str, call_id: str, store: CaseStore = Depends(get_store), voice: httpx.Client = Depends(get_voice), user: str = Depends(current_user)):
    _case(store, case_id, user)
    _owner_only(user)
    try:
        r = voice.post(f"/phone/hangup/{call_id}")
    except httpx.HTTPError:
        raise HTTPException(status_code=503, detail="the voice server is not reachable")
    if r.status_code == 404:
        return {"ended": True, "note": "the call was already over"}
    return {"ended": r.status_code == 200}


@router.get("/{case_id}/call/events")
def events(case_id: str, since: int = 0, store: CaseStore = Depends(get_store), voice: httpx.Client = Depends(get_voice), user: str = Depends(current_user)):
    _case(store, case_id, user)
    _owner_only(user)
    try:
        r = voice.get("/voice/events", params={"since": since})
    except httpx.HTTPError:
        raise HTTPException(status_code=503, detail="the voice server is not reachable")
    out = []
    for e in r.json():
        text, _ = redact(str(e.get("text", "")), strict=True)
        out.append({"n": e.get("n"), "kind": e.get("kind"), "text": text, "t": e.get("t")})
    return out
