import pytest

from app.directory.loader import load_companies
from app.directory.lookup import find_company
from app.directory.picker import pick_contact, resolve_channel
from app.evaluation import load_problems
from app.models.case import Channel

COMPANIES = load_companies()


def test_picked_contacts_come_from_the_directory_with_sources():
    for c in COMPANIES:
        choice = pick_contact(c)
        listed = {h.value for h in (*c.helplines, *c.emails)} | ({c.grievance_officer.email} if c.grievance_officer else set())
        for item in (choice.phone, choice.support_email, choice.grievance_email):
            if item:
                assert item.value in listed, f"{c.name}: {item.value} is not a directory contact"
                assert item.source_url.startswith("https://") and item.source_quote


def test_channels_match_what_exists():
    for c in COMPANIES:
        ch = pick_contact(c)
        assert (Channel.call in ch.channels_available) == (ch.phone is not None)
        if Channel.complaint in ch.channels_available:
            assert ch.grievance_email is not None
        if ch.no_phone_notice:
            assert ch.phone is None, f"{c.name} says it has no phone line but we picked a phone"


@pytest.mark.parametrize("name", ["Swiggy", "Zomato", "Zepto"])
def test_companies_with_no_phone_line_never_get_a_call(name):
    ch = pick_contact(find_company(name))
    assert Channel.call not in ch.channels_available
    assert ch.no_phone_notice


def test_airtel_and_vi_use_the_complaints_line_first():
    assert pick_contact(find_company("Airtel")).phone.value == "198"
    assert pick_contact(find_company("Vi")).phone.value == "198"


def test_grievance_and_nodal_lines_are_not_used_as_the_customer_phone():
    assert pick_contact(find_company("Uber")).phone.value == "+91 891 451 2030"
    assert pick_contact(find_company("Flipkart")).phone is None   # only office and grievance lines exist


def test_credit_card_complaint_email_is_not_the_general_support_email():
    assert pick_contact(find_company("HDFC Bank")).support_email is None


def test_warnings_for_single_source_and_needs_check():
    ch = pick_contact(find_company("Airtel"))
    assert any("only one official page" in w for w in ch.warnings)
    assert any("needs_check" in w for w in pick_contact(find_company("Jio")).warnings)


def test_resolve_channel_fallbacks():
    swiggy = pick_contact(find_company("Swiggy"))
    assert resolve_channel(Channel.call, swiggy)[0] == Channel.email
    assert resolve_channel(Channel.email, swiggy) == (Channel.email, None)
    empty = pick_contact(find_company("Myntra"))
    ch, why = resolve_channel(Channel.call, empty)
    assert ch is None and "no verified contact" in why
    airtel = pick_contact(find_company("Airtel"))
    assert resolve_channel(Channel.email, airtel)[0] == Channel.call


def test_every_named_company_in_the_30_problems_gets_a_contact_or_a_clear_reason():
    no_contact = []
    for p in load_problems():
        name = p["expected"]["company"]
        if not name:
            continue
        company = find_company(name) or next((find_company(a) for a in p["expected"].get("company_aliases", []) if find_company(a)), None)
        assert company, f"{name} not in directory"
        if not pick_contact(company).channels_available:
            no_contact.append(company.name)
    # known gaps (needs_check): these are honest "no verified contact yet", not guesses
    assert set(no_contact) <= {"Myntra", "BSNL", "Ola"}, no_contact
