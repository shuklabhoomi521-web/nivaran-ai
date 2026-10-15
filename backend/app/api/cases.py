from fastapi import APIRouter, Depends, HTTPException

from app.brain.llm import AnthropicLLM, LLMClient, LLMError
from app.brain.plan import make_plan
from app.brain.understand import understand
from app.config import ConfigError
from app.models.case import Plan, PlanRequest, UnderstandRequest, UnderstandResponse

router = APIRouter(prefix="/cases", tags=["cases"])


def get_llm() -> LLMClient:
    try:
        return AnthropicLLM()
    except ConfigError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/understand", response_model=UnderstandResponse)
def understand_case(req: UnderstandRequest, llm: LLMClient = Depends(get_llm)):
    if not req.message.strip():
        raise HTTPException(status_code=422, detail="message is empty")
    try:
        return understand(req.message, llm)
    except LLMError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/plan", response_model=Plan)
def plan_case(req: PlanRequest, llm: LLMClient = Depends(get_llm)):
    if req.case.company is None:
        raise HTTPException(status_code=422, detail="company is unknown: ask the user first")
    try:
        return make_plan(req.case, llm)
    except LLMError as e:
        raise HTTPException(status_code=502, detail=str(e))
