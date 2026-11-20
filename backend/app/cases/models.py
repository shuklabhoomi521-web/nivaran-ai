"""A tracked case: what the user asked, what we did, and what happened, as an append-only timeline.
(`app.models.case.Case` is what the AI understood from the user's words; this is the case file that lives on for days.)"""
from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.models.case import Category, Fact, UserGoal


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CaseState(str, Enum):
    new = "new"                # created, nothing sent yet
    waiting = "waiting"        # we contacted the company, waiting for a reply
    escalated = "escalated"    # we went above the first line (grievance officer, appellate authority or regulator)
    resolved = "resolved"      # the user says it is solved
    closed = "closed"          # the user stopped without a solution


OPEN_STATES = {CaseState.new, CaseState.waiting, CaseState.escalated}


class Rung(str, Enum):
    """The escalation ladder, lowest to highest."""
    first_contact = "first_contact"          # day 0: the company's own support line
    follow_up = "follow_up"                  # day 3: same channel, shorter, quotes the first message
    grievance_officer = "grievance_officer"  # day 7: the grievance or nodal officer
    appellate = "appellate"                  # day 15: the appellate authority (if the company has one)
    regulator = "regulator"                  # day 15 when there is no appellate authority: the regulator's portal


class EventKind(str, Enum):
    contacted = "contacted"            # we (or the user) sent a message or made a call
    reply_received = "reply_received"  # the company answered
    note = "note"                      # a free note, for example a docket number
    resolved = "resolved"
    closed = "closed"


class Event(Strict):
    on: date
    kind: EventKind
    rung: Rung | None = None           # for `contacted`: which rung this contact belongs to
    channel: str | None = None         # "email", "call", "portal", "chat"
    text: str = ""                     # short note: what was sent, what they said, the docket number
    docket: str | None = None          # a complaint or docket number, if one was given


class TrackedCase(Strict):
    id: str
    company: str
    category: Category
    problem_summary: str
    user_goal: UserGoal
    facts: list[Fact] = Field(default_factory=list)     # only facts the user gave: letters may use nothing else
    created_on: date
    state: CaseState = CaseState.new
    events: list[Event] = Field(default_factory=list)

    @property
    def is_open(self) -> bool:
        return self.state in OPEN_STATES

    def done_rungs(self) -> set[Rung]:
        return {e.rung for e in self.events if e.kind == EventKind.contacted and e.rung is not None}


class Action(Strict):
    """What should happen next on a case."""
    rung: Rung
    due_on: date
    days_overdue: int                  # 0 when not yet late
    channel: str                       # "email", "call", "portal", "chat"
    target_label: str                  # who or where (for example "Grievance officer", "RBI Complaint Management System")
    target_value: str | None           # an email, a number or a link from the verified directory (None = nothing to send to)
    source_url: str | None             # the official page that shows the target
    source_quote: str | None
    reason: str                        # one plain sentence the app can show
    fell_back_from: Rung | None = None # set when the planned rung had no verified target and we moved up
    note: str | None = None            # extra plain-language note, for example why the first contact is the grievance address
