from app.directory.loader import load_companies
from app.directory.models import ChatChannel, ChatKind, Regulator, Source
from app.directory.regulators import FALLBACK_KEY, load_regulators, regulator_for
from app.models.case import Category
import pytest


def test_every_category_gets_a_verified_regulator():
    for cat in Category:
        r = regulator_for(cat)
        assert r.source is not None and r.source.quote.strip() and r.source.url.startswith("https://")


def test_specific_regulators_are_chosen_where_verified():
    assert regulator_for(Category.banking_upi).key == "rbi_cms"
    assert regulator_for(Category.insurance).key == "irdai_bima_bharosa"
    assert regulator_for(Category.telecom).key == "trai_telecom"
    assert regulator_for(Category.railways).key == "rail_madad"
    assert regulator_for(Category.food_delivery).key == FALLBACK_KEY


def test_airsewa_is_used_for_airlines_and_still_lists_what_is_unverified():
    airsewa = next(r for r in load_regulators() if r.key == "airsewa")
    assert airsewa.source is not None and "AirSewa enables travelers" in airsewa.source.quote and airsewa.needs_check
    assert regulator_for(Category.airlines).key == "airsewa"
    assert all(st.ours or st.source for st in airsewa.steps)          # every step is an official line or labelled as ours


def test_a_regulator_without_source_must_explain():
    with pytest.raises(ValueError):
        Regulator(key="x", name="X", portal_url="https://x.test/", covers=[], what_for="x")
    with pytest.raises(ValueError):
        Regulator(key="x", name="X", portal_url="http://x.test/", covers=[], what_for="x", needs_check=["why"])


def test_existing_companies_still_load_with_v2_fields_empty():
    cs = load_companies()
    first40 = cs[:40]                 # the original entries do not use the new fields
    assert len(cs) >= 45 and all(c.appellate_authority is None and c.chat_channels == [] for c in first40)


def test_chat_channel_needs_a_source():
    s = Source(url="https://x.test/help", kind="website", quote="Chat with us", checked_on="2026-11-20")
    assert ChatChannel(kind=ChatKind.whatsapp, value="https://wa.me/910000000000", sources=[s]).kind == ChatKind.whatsapp
    with pytest.raises(ValueError):
        ChatChannel(kind=ChatKind.web_chat, value="https://x.test/chat")
