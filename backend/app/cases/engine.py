"""The case engine: pure functions, no database, no AI. Same inputs, same answer, easy to test.

The ladder days are DEFAULTS chosen by us (not legal advice): day 0 first contact, day 3 follow-up, day 7 grievance officer,
day 15 appellate authority or regulator. Some regulators ask people to wait longer before filing; the regulator text we show
comes from the verified table in `app.directory.regulators`."""
import uuid
from datetime import date, timedelta

from app.cases.models import Action, CaseState, Event, EventKind, Rung, TrackedCase
from app.directory.models import Company
from app.directory.picker import pick_contact
from app.directory.regulators import regulator_for
from app.models.case import Case

ORDER: tuple[Rung, ...] = (Rung.first_contact, Rung.follow_up, Rung.grievance_officer, Rung.appellate, Rung.regulator)
DAYS: dict[Rung, int] = {Rung.first_contact: 0, Rung.follow_up: 3, Rung.grievance_officer: 7, Rung.appellate: 15, Rung.regulator: 15}


class CaseError(ValueError):
    pass


def new_case(understood: Case, today: date, case_id: str | None = None, user_name: str | None = None) -> TrackedCase:
    """Start a case file from what the AI understood. The company must be known: we never guess who to write to."""
    if not understood.company:
        raise CaseError("the company is unknown: ask the user first")
    return TrackedCase(id=case_id or uuid.uuid4().hex[:12], company=understood.company, category=understood.category,
                       problem_summary=understood.problem_summary, user_goal=understood.user_goal,
                       facts=list(understood.details_known), created_on=today, user_name=user_name)


def apply(case: TrackedCase, event: Event) -> TrackedCase:
    """Add one event and return the new case file. The old object is not changed."""
    if not case.is_open:
        raise CaseError(f"the case is {case.state.value}; no more events can be added")
    if event.on < case.created_on:
        raise CaseError("an event cannot be older than the case")
    if event.kind == EventKind.contacted and event.rung is None:
        raise CaseError("a contact must say which rung of the ladder it belongs to")
    if event.kind == EventKind.contacted and ORDER.index(event.rung) <= _done_index(case):
        raise CaseError(f"the {event.rung.value} step is already done or was skipped upward")
    state = case.state
    if event.kind == EventKind.contacted:
        state = CaseState.waiting if event.rung in (Rung.first_contact, Rung.follow_up) else CaseState.escalated
        if case.state == CaseState.escalated:
            state = CaseState.escalated          # never step back down
    elif event.kind == EventKind.resolved:
        state = CaseState.resolved
    elif event.kind == EventKind.closed:
        state = CaseState.closed
    return case.model_copy(update={"state": state, "events": [*case.events, event]})


def due_date(case: TrackedCase, rung: Rung) -> date:
    return case.created_on + timedelta(days=DAYS[rung])


def _done_index(case: TrackedCase) -> int:
    """Index in ORDER of the highest rung already used. Anything at or below it counts as done, so a step skipped upward is not repeated."""
    idx = [ORDER.index(r) for r in case.done_rungs()]
    return max(idx) if idx else -1


def _target_for(rung: Rung, company: Company | None, case: TrackedCase) -> tuple[str, str, str | None, str | None, str | None]:
    """(channel, label, value, source_url, source_quote) for a rung, from the verified directory only. value None = nothing verified."""
    choice = pick_contact(company) if company else None
    if rung in (Rung.first_contact, Rung.follow_up):
        if choice and choice.support_email:
            c = choice.support_email
            return "email", c.label or "Customer support email", c.value, c.source_url, c.source_quote
        if choice and choice.phone:
            c = choice.phone
            return "call", c.label or "Customer care phone", c.value, c.source_url, c.source_quote
        return "email", "Customer support", None, None, None
    if rung == Rung.grievance_officer:
        if choice and choice.grievance_email:
            c = choice.grievance_email
            return "email", c.label or "Grievance officer", c.value, c.source_url, c.source_quote
        return "email", "Grievance officer", None, None, None
    if rung == Rung.appellate:
        a = company.appellate_authority if company else None
        if a and a.email:
            s = a.sources[0]
            return "email", "Appellate authority", a.email, s.url, s.quote
        return "email", "Appellate authority", None, None, None
    r = regulator_for(case.category)
    return "portal", r.name, r.portal_url, r.source.url if r.source else None, r.source.quote if r.source else None


def next_action(case: TrackedCase, today: date, company: Company | None) -> Action | None:
    """The one thing to do next, or None when the case is closed, solved, or the ladder is finished.
    A grievance or appellate rung with no verified target is skipped upward (ending at the regulator), and the action says so."""
    if not case.is_open:
        return None
    start = _done_index(case) + 1
    if start >= len(ORDER):
        return None
    planned = ORDER[start]
    due = due_date(case, planned)
    rung = planned
    channel, label, value, url, quote = _target_for(rung, company, case)
    fell = None
    note = None
    if value is None and rung in (Rung.first_contact, Rung.follow_up):
        # no customer-support contact is listed (some companies only publish a grievance address): use that, and say so
        g_channel, g_label, g_value, g_url, g_quote = _target_for(Rung.grievance_officer, company, case)
        if g_value is not None:
            channel, label, value, url, quote = g_channel, g_label, g_value, g_url, g_quote
            note = "No customer-support contact is listed for this company, so the official grievance address is used for the first message."
        elif company and company.channel_notes:
            note = company.channel_notes
    while value is None and rung in (Rung.grievance_officer, Rung.appellate):
        fell = fell or planned
        rung = ORDER[ORDER.index(rung) + 1]
        channel, label, value, url, quote = _target_for(rung, company, case)
    late = (today - due).days
    reason = _reason(rung, case, today - due) if late >= 0 else f"Nothing is due yet. The next step is on {due.isoformat()}."
    return Action(rung=rung, due_on=due, days_overdue=max(late, 0), channel=channel, target_label=label, target_value=value,
                  source_url=url, source_quote=quote, fell_back_from=fell, reason=reason, note=note)


def _reason(rung: Rung, case: TrackedCase, late: timedelta) -> str:
    if rung == Rung.first_contact:
        return "Send the first message now, with the facts the user gave."
    if rung == Rung.follow_up:
        return "No solution yet: send a short follow-up that quotes the first message."
    if rung == Rung.grievance_officer:
        return "Still unsolved: write to the grievance officer with the full history."
    if rung == Rung.appellate:
        return "Still unsolved: go to the appellate authority."
    return "Still unsolved: file the complaint on the regulator's official portal and keep the docket number."


def reminders(case: TrackedCase, today: date) -> list[dict]:
    """The whole ladder as a list the app can show: each step, its date, and whether it is done, due or upcoming."""
    done_idx = _done_index(case)
    out = []
    for i, rung in enumerate(ORDER):
        due = due_date(case, rung)
        if i <= done_idx:
            status = "done"
        elif not case.is_open:
            status = "closed"
        else:
            status = "due" if today >= due else "upcoming"
        out.append({"rung": rung.value, "due_on": due.isoformat(), "status": status})
    return out
