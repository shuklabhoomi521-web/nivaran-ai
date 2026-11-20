"""The company directory: official contacts only. Every contact carries the exact line of text
from the official page where it was found, so a person can check it in seconds."""
import re
from datetime import date
from enum import Enum
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.models.case import Category


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SourceKind(str, Enum):
    website = "website"          # the company's own site (main, help. or support. subdomain, or a listed parent/support domain)
    play_store = "play_store"    # the company's official Play Store listing
    regulator = "regulator"      # a regulator or government page that names the contact (e.g. RBI, TRAI, consumer affairs)


STORE_HOSTS = {"play.google.com"}


class Source(Strict):
    url: str
    kind: SourceKind
    quote: str            # the exact line from the page (copied, not reworded)
    checked_on: date
    machine_checked: bool = False   # True = our script re-fetched the page and found this exact line

    @property
    def host(self) -> str:
        return (urlparse(self.url).hostname or "").lower()


class ContactKind(str, Enum):
    phone = "phone"
    email = "email"


class ContactPoint(Strict):
    kind: ContactKind
    value: str
    label: str | None = None      # e.g. "Customer care", "Grievance officer"
    hours: str | None = None
    role: str | None = None       # "complaints" (a line for complaints), "sales", "officer" (an officer's own line), "senior"
    sources: list[Source]

    @property
    def confirmation(self) -> str:
        """two_sources = found on 2 different official pages; single_source = only 1."""
        return "two_sources" if len({s.url for s in self.sources}) >= 2 else "single_source"


class GrievanceOfficer(Strict):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    sources: list[Source]


class ChatKind(str, Enum):
    in_app = "in_app"
    web_chat = "web_chat"
    whatsapp = "whatsapp"


class ChatChannel(Strict):
    kind: ChatKind
    value: str                    # a link or a number the company itself publishes
    label: str | None = None
    sources: list[Source]


class KitItem(Strict):
    """One line of a portal kit. Either it is backed by an exact quote from an official page (`source`), or it is our own checklist
    advice and says so (`ours=True`). Nothing else is allowed, so an unverified rule can never look like an official one."""
    text: str
    source: Source | None = None
    ours: bool = False

    @model_validator(mode="after")
    def _sourced_or_ours(self):
        if self.source is None and not self.ours:
            raise ValueError("a kit item needs an official source or must be marked as our own advice")
        if self.source is not None and self.ours:
            raise ValueError("a kit item is either official (has a source) or ours, not both")
        return self


class Regulator(Strict):
    """Where a complaint goes when the company does not solve it. Every entry carries the official page and an exact quote;
    if we could not read the official page, `source` is empty and `needs_check` says what is still unverified."""
    key: str
    name: str
    portal_url: str
    covers: list[Category]
    what_for: str
    helpline: str | None = None
    source: Source | None = None
    steps: list[KitItem] = []         # how to file, in order
    attach: list[KitItem] = []        # what to prepare or attach
    needs_check: list[str] = []

    @field_validator("portal_url")
    @classmethod
    def _https(cls, v: str) -> str:
        if not v.startswith("https://"):
            raise ValueError("portal_url must be https")
        return v

    @model_validator(mode="after")
    def _honest(self):
        if self.source is None and not self.needs_check:
            raise ValueError("a regulator without a verified source must say what is unverified (needs_check)")
        return self


class Company(Strict):
    name: str
    aliases: list[str]
    category: Category
    official_domains: list[str]   # main domain plus allowed parent / support domains
    source_url: str               # the main official page for this company's contacts
    checked_on: date
    helplines: list[ContactPoint]
    emails: list[ContactPoint]
    grievance_officer: GrievanceOfficer | None = None
    working_hours: str | None = None
    channel_notes: str | None = None
    appellate_authority: GrievanceOfficer | None = None   # v2: the appellate authority named on the company's official page
    chat_channels: list[ChatChannel] = []                # v2: in-app, web chat or WhatsApp the company itself publishes
    official_no_phone: Source | None = None   # the official page saying the company has NO customer phone line
    needs_check: list[str] = []   # things we could not confirm: the founder must fill or drop them

    @field_validator("source_url")
    @classmethod
    def _https(cls, v: str) -> str:
        if not v.startswith("https://"):
            raise ValueError("source_url must be https")
        return v


def digits(text: str) -> str:
    return re.sub(r"\D", "", text)


def host_allowed(host: str, domains: list[str]) -> bool:
    host = host.lower()
    return any(host == d or host.endswith("." + d) for d in (x.lower() for x in domains))
