"""Portal kit: everything the user needs to file a complaint on the regulator's official portal by hand.
Official lines carry an exact quote from an official page; our own checklist is labelled as ours; anything unverified is listed as needs-check."""
from datetime import date

from pydantic import BaseModel, ConfigDict

from app.cases.models import Action, Rung, TrackedCase
from app.directory.models import KitItem
from app.directory.regulators import load_regulators, regulator_for
from app.letters.compose import compose


class PortalKit(BaseModel):
    model_config = ConfigDict(extra="forbid")
    regulator_key: str
    regulator: str
    portal_url: str
    helpline: str | None
    purpose: str                      # one plain sentence
    purpose_source_url: str | None
    purpose_quote: str | None
    steps: list[KitItem]              # official steps, each with its quote
    official_attach: list[KitItem]
    checklist: list[str]              # our own checklist, always labelled as ours by the app
    complaint_text: str               # ready to paste on the portal
    warnings: list[str]
    needs_check: list[str]


def build_kit(case: TrackedCase, today: date) -> PortalKit:
    reg = regulator_for(case.category)
    action = Action(rung=Rung.regulator, due_on=today, days_overdue=0, channel="portal", target_label=reg.name, target_value=reg.portal_url,
                    source_url=reg.source.url if reg.source else None, source_quote=reg.source.quote if reg.source else None, reason="File on the portal")
    letter = compose(case, action, today)           # raises LetterError if payment data would be pasted
    checklist = [f"Your case reference ({case.id}) and the dates you contacted the company (the complaint text lists them).",
                 "Screenshots or copies of every reply the company sent, if any.",
                 "Any ticket or docket number the company gave you.",
                 "Proof of the problem and of payment as screenshots or a PDF. Hide card numbers on them."]
    if case.facts:
        checklist.insert(1, "The details you gave us: " + ", ".join(f.name.replace("_", " ") for f in case.facts) + ".")
    checklist.append("After you file, write the docket number into this case as a note so we can remind you to check it.")
    warnings = ["Nivaran never types a password, OTP, PIN or card detail on a portal for you. You file it yourself.",
                "The official lines come from the pages quoted next to them. Portals change: check the page before you rely on a rule."]
    needs = list(reg.needs_check)
    for other in load_regulators():                 # a regulator for this category that we could not verify is shown, not hidden
        if other.key != reg.key and case.category in other.covers and other.source is None:
            needs.append(f"{other.name} also covers this category but could not be verified, so the helpline above is used: " + "; ".join(other.needs_check))
    return PortalKit(regulator_key=reg.key, regulator=reg.name, portal_url=reg.portal_url, helpline=reg.helpline, purpose=reg.what_for,
                     purpose_source_url=reg.source.url if reg.source else None, purpose_quote=reg.source.quote if reg.source else None,
                     steps=reg.steps, official_attach=reg.attach, checklist=checklist, complaint_text=letter.body, warnings=warnings, needs_check=needs)
