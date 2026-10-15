from fastapi import APIRouter, Depends, HTTPException

from app.brain.llm import LLMClient, LLMError, make_llm
from app.brain.ratelimit import DailyQuotaExceeded
from app.brain.plan import make_plan
from app.brain.understand import understand
from app.config import ConfigError
from app.directory.lookup import find_company
from app.directory.picker import pick_contact, resolve_channel
from app.models.case import PlanRequest, UnderstandRequest, UnderstandResponse
from app.models.planning import PlanResponse

router = APIRouter(prefix="/cases", tags=["cases"])


def get_llm() -> LLMClient:
    try:
        return make_llm()
    except ConfigError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/understand", response_model=UnderstandResponse)
def understand_case(req: UnderstandRequest, llm: LLMClient = Depends(get_llm)):
    if not req.message.strip():
        raise HTTPException(status_code=422, detail="message is empty")
    try:
        return understand(req.message, llm)
    except DailyQuotaExceeded as e:
        raise HTTPException(status_code=429, detail=str(e))
    except LLMError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/plan", response_model=PlanResponse)
def plan_case(req: PlanRequest, llm: LLMClient = Depends(get_llm)):
    if req.case.company is None:
        raise HTTPException(status_code=422, detail="company is unknown: ask the user first")
    company = find_company(req.case.company)
    choice = pick_contact(company) if company else None
    try:
        plan = make_plan(req.case, llm,
                         available_channels=choice.channels_available if choice and choice.channels_available else None,
                         no_phone_line=bool(choice and choice.no_phone_notice))
    except DailyQuotaExceeded as e:
        raise HTTPException(status_code=429, detail=str(e))
    except LLMError as e:
        raise HTTPException(status_code=502, detail=str(e))
    if choice is None:
        return PlanResponse(plan=plan, channel=None, channel_note=None, contact=None, can_proceed=False,
                            note=f"{req.case.company} is not in our verified directory. We never use a number from a web search.")
    channel, why = resolve_channel(plan.channel, choice)
    if channel is None:
        return PlanResponse(plan=plan, channel=None, channel_note=why, contact=choice, can_proceed=False,
                            note="The directory has no verified contact for this company yet.")
    return PlanResponse(plan=plan, channel=channel, channel_note=why, contact=choice, can_proceed=True, note=None)
