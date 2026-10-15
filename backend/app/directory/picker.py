"""Picks the official contact for a case from the verified directory. The AI never invents a number:
every phone and email returned here is a directory entry with its source link and exact quote."""
import re

from pydantic import BaseModel

from app.directory.models import Company, ContactKind, ContactPoint
from app.models.case import Channel

_NOT_FOR_CALLS = re.compile(r"whatsapp|outside india|nodal|appellate|grievance|senior|head office|investor|corporate|office line", re.I)
_ESCALATION = re.compile(r"grievance|nodal|appellate", re.I)
_NOT_SUPPORT = re.compile(r"grievance|nodal|appellate|investor|security|data and consent|mis-selling|harassment|public relations|ucc", re.I)
_SKIP_ROLES = {"sales", "officer", "senior"}   # never the first phone to call about a complaint


class ContactItem(BaseModel):
    value: str
    label: str | None
    hours: str | None
    confirmation: str          # "two_sources" or "single_source"
    source_url: str
    source_quote: str
    machine_checked: bool


class ContactChoice(BaseModel):
    company: str
    channels_available: list[Channel]
    phone: ContactItem | None
    support_email: ContactItem | None
    grievance_email: ContactItem | None
    no_phone_notice: str | None     # the official sentence saying there is no customer phone line
    notes: str | None
    directory_page: str
    warnings: list[str]


def _item(cp: ContactPoint) -> ContactItem:
    s = cp.sources[0]
    return ContactItem(value=cp.value, label=cp.label, hours=cp.hours, confirmation=cp.confirmation,
                       source_url=s.url, source_quote=s.quote, machine_checked=all(x.machine_checked for x in cp.sources))


def pick_contact(company: Company) -> ContactChoice:
    callable_ = [p for p in company.helplines if p.role not in _SKIP_ROLES and not (p.role is None and _NOT_FOR_CALLS.search(p.label or ""))]
    # a line made for complaints (role "complaints" or "Complaints" in its label) comes first
    phone = next((p for p in callable_ if p.role == "complaints" or re.search("complaint", p.label or "", re.I)), None) \
        or (callable_[0] if callable_ else None)
    support = next((e for e in company.emails if not _NOT_SUPPORT.search(e.label or "")), None)
    escalation = next((e for e in company.emails if _ESCALATION.search(e.label or "")), None)
    if escalation is None and company.grievance_officer and company.grievance_officer.email:
        s = company.grievance_officer.sources[0]
        escalation_item = ContactItem(value=company.grievance_officer.email, label="Grievance officer", hours=None,
                                      confirmation="single_source", source_url=s.url, source_quote=s.quote,
                                      machine_checked=s.machine_checked)
    else:
        escalation_item = _item(escalation) if escalation else None

    channels = []
    if phone:
        channels.append(Channel.call)
    if support or escalation_item:
        channels.append(Channel.email)
    if escalation_item:
        channels.append(Channel.complaint)

    warnings = []
    if phone and phone.confirmation == "single_source":
        warnings.append("phone number found on only one official page")
    if phone and not all(s.machine_checked for s in phone.sources):
        warnings.append("phone line was read in a browser, not re-checked by script")
    if company.needs_check:
        warnings.append("directory entry has unresolved needs_check items")
    if not channels:
        warnings.append("no verified contact in the directory yet")
    return ContactChoice(
        company=company.name, channels_available=channels,
        phone=_item(phone) if phone else None,
        support_email=_item(support) if support else None,
        grievance_email=escalation_item,
        no_phone_notice=company.official_no_phone.quote if company.official_no_phone else None,
        notes=company.channel_notes, directory_page=company.source_url, warnings=warnings)


_FALLBACK = {Channel.call: [Channel.email, Channel.complaint], Channel.email: [Channel.complaint, Channel.call],
             Channel.complaint: [Channel.email, Channel.call]}


def resolve_channel(suggested: Channel, choice: ContactChoice) -> tuple[Channel | None, str | None]:
    """Keep the AI's channel if the directory supports it, otherwise the nearest one that exists."""
    if suggested in choice.channels_available:
        return suggested, None
    for alt in _FALLBACK[suggested]:
        if alt in choice.channels_available:
            return alt, f"{suggested.value} is not possible for {choice.company} (no verified {suggested.value} contact); using {alt.value}"
    return None, f"no verified contact for {choice.company}"
