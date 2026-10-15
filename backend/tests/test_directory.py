import re
from datetime import date

import pytest

from app.directory.loader import load_companies
from app.directory.lookup import find_company
from app.directory.models import SourceKind, digits, host_allowed
from app.evaluation import load_problems

COMPANIES = load_companies()
ALL_CONTACTS = [(c, h) for c in COMPANIES for h in (*c.helplines, *c.emails)]


def all_sources(c):
    out = [s for h in (*c.helplines, *c.emails) for s in h.sources]
    if c.grievance_officer:
        out += c.grievance_officer.sources
    if c.official_no_phone:
        out.append(c.official_no_phone)
    return out


def test_names_and_aliases_are_unique():
    seen = {}
    for c in COMPANIES:
        for n in [c.name, *c.aliases]:
            key = re.sub(r"[\W_]+", "", n.casefold())
            assert seen.setdefault(key, c.name) == c.name, f"{n} used by {seen[key]} and {c.name}"


@pytest.mark.parametrize("c", COMPANIES, ids=[c.name for c in COMPANIES])
def test_every_source_is_official_https_and_dated(c):
    assert c.source_url.startswith("https://")
    assert host_allowed(c.source_url.split("/")[2], c.official_domains), "main page is not on an official domain"
    for s in all_sources(c):
        assert s.url.startswith("https://"), s.url
        if s.kind == SourceKind.website:
            assert host_allowed(s.host, c.official_domains), f"{c.name}: {s.url} is not an official domain"
        assert s.checked_on <= date.today()
        assert (date.today() - s.checked_on).days < 366, "source is more than a year old"
        assert s.quote.strip()
    assert c.checked_on <= date.today()


@pytest.mark.parametrize("c,h", ALL_CONTACTS, ids=[f"{c.name}:{h.value}" for c, h in ALL_CONTACTS])
def test_every_contact_appears_in_its_exact_quote(c, h):
    assert h.sources, "a contact with no source is not allowed"
    for s in h.sources:
        if h.kind.value == "email":
            assert h.value.lower() in s.quote.lower()
        else:
            assert digits(h.value) in digits(s.quote)


@pytest.mark.parametrize("c", COMPANIES, ids=[c.name for c in COMPANIES])
def test_company_has_a_contact_or_a_reason(c):
    has_contact = c.helplines or c.emails or c.grievance_officer or c.official_no_phone
    assert has_contact or c.needs_check, f"{c.name} has nothing: add a contact or a needs_check note"


def test_confirmation_label():
    flipkart = find_company("flipkart")
    by_value = {h.value: h for h in flipkart.helplines}
    assert by_value["044-67415800"].confirmation == "two_sources"
    assert by_value["044-45614700"].confirmation == "single_source"


def test_lookup_handles_spelling_case_and_aliases():
    assert find_company("swiggy").name == "Swiggy"
    assert find_company("  SWIGGY ").name == "Swiggy"
    assert find_company("Vodafone Idea").name == "Vi"
    assert find_company("indigo airlines").name == "IndiGo"
    assert find_company("Nonexistent Corp") is None
    assert find_company(None) is None
    assert find_company("") is None


@pytest.mark.xfail(reason="Phase 2 in progress: 40 companies not reached yet", strict=False)
def test_forty_companies_across_ten_categories():
    assert len(COMPANIES) >= 40
    assert len({c.category for c in COMPANIES}) >= 10


@pytest.mark.xfail(reason="Phase 2 in progress: all test-set companies not added yet", strict=False)
def test_every_company_in_the_30_problems_is_in_the_directory():
    missing = []
    for p in load_problems():
        name = p["expected"]["company"]
        if name and find_company(name) is None:
            aliases = p["expected"].get("company_aliases", [])
            if not any(find_company(a) for a in aliases):
                missing.append(name)
    assert not missing, sorted(set(missing))
