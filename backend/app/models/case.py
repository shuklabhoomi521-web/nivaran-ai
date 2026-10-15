from enum import Enum

from pydantic import BaseModel, ConfigDict


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Category(str, Enum):
    food_delivery = "food_delivery"
    ecommerce = "ecommerce"
    telecom = "telecom"
    banking_upi = "banking_upi"
    airlines = "airlines"
    railways = "railways"
    cabs = "cabs"
    electronics_appliances = "electronics_appliances"
    insurance = "insurance"
    utilities = "utilities"
    other = "other"


class UserGoal(str, Enum):
    refund = "refund"
    repair = "repair"
    replace = "replace"
    cancel = "cancel"
    info = "info"
    other = "other"


class Language(str, Enum):
    english = "english"
    hindi = "hindi"
    tamil = "tamil"
    telugu = "telugu"
    kannada = "kannada"
    malayalam = "malayalam"
    bengali = "bengali"
    marathi = "marathi"
    gujarati = "gujarati"
    punjabi = "punjabi"
    hinglish = "hinglish"
    other = "other"


class Urgency(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Confidence(str, Enum):
    high = "high"
    low = "low"


class Fact(Strict):
    name: str
    value: str


class Case(Strict):
    company: str | None
    category: Category
    category_confidence: Confidence
    problem_summary: str
    user_goal: UserGoal
    details_known: list[Fact]
    details_missing: list[str]
    user_language: Language
    urgency: Urgency
    other_issues: list[str]


class UnderstandOutput(Case):
    """What Claude fills in: the case plus one optional follow-up question."""

    follow_up_question: str | None


class UnderstandRequest(BaseModel):
    message: str


class UnderstandResponse(BaseModel):
    case: Case
    follow_up_question: str | None
    redacted: list[str]  # kinds of private data removed before the AI saw the text


class Channel(str, Enum):
    call = "call"
    email = "email"
    complaint = "complaint"


class Plan(Strict):
    channel: Channel
    reason: str
    opening_line: str
    proof_to_keep: list[str]


class PlanRequest(BaseModel):
    case: Case
