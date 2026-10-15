"""The company directory: official contacts only. Every contact carries the exact line of text
from the official page where it was found, so a person can check it in seconds."""
import re
from datetime import date
from enum import Enum
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, field_validator

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
