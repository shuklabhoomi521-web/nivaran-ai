from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.api import tracked
from app.cases import engine
from app.cases.kit import build_kit
from app.cases.store import CaseStore
from app.directory.models import KitItem, Source
from app.directory.regulators import load_regulators
from app.letters.compose import LetterError
from app.main import app
from app.models.case import Case, Category, Confidence, Fact, Language, Urgency, UserGoal

D0 = date(2026, 12, 20)


def case(category=Category.food_delivery, facts=None, company="Swiggy"):
    u = Case(company=company, category=category, category_confidence=Confidence.high, problem_summary="Refund not given.", user_goal=UserGoal.refund,
             details_known=facts if facts is not None else [Fact(name="order_id", value="4839201")], details_missing=[],
             user_language=Language.english, urgency=Urgency.low, other_issues=[])
    return engine.new_case(u, D0, "k1", user_name="Bhoomi Shukla")


def test_every_kit_line_is_official_with_a_quote_or_labelled_ours():
    for r in load_regulators():
        for item in (*r.steps, *r.attach):
            assert (item.source is not None and item.source.quote.strip() and item.source.url.startswith("https://")) != item.ours
            if item.source:
                assert item.source.kind.value == "regulator"
    with pytest.raises(ValueError):
        KitItem(text="made up rule")                                   # no source and not marked ours
    s = Source(url="https://x.test/", kind="regulator", quote="q", checked_on="2026-11-20")
    with pytest.raises(ValueError):
        KitItem(text="both", source=s, ours=True)
    assert KitItem(text="our advice", ours=True).ours


def test_kit_for_a_consumer_case_uses_the_national_helpline_and_pastes_the_facts():
    k = build_kit(case(), D0)
    assert k.regulator_key == "nch" and k.portal_url.startswith("https://consumerhelpline.gov.in") and "1915" in (k.helpline or "")
    assert len(k.steps) >= 5 and all(s.source for s in k.steps)
    assert "Complaint against Swiggy" in k.complaint_text and "order id: 4839201" in k.complaint_text and "Case reference: k1" in k.complaint_text
    assert any("docket number" in c for c in k.checklist) and any("order id" in c for c in k.checklist)
    assert any("never types a password, OTP" in w for w in k.warnings)


def test_insurance_and_bank_kits_pick_their_regulators_and_flag_what_is_unverified():
    ins = build_kit(case(Category.insurance, company="LIC"), D0)
    assert ins.regulator_key == "irdai_bima_bharosa" and any("first complain to the insurer" in s.text.lower() for s in ins.steps)
    assert any("reasonable period" in n for n in ins.needs_check)
    bank = build_kit(case(Category.banking_upi, company="SBI"), D0)
    assert bank.regulator_key == "rbi_cms" and bank.helpline == "#14448" and any("scheme" in n for n in bank.needs_check)    # bank-first rule NOT claimed


def test_unverified_regulator_is_shown_not_hidden():
    air = build_kit(case(Category.airlines, company="IndiGo"), D0)
    assert air.regulator_key == "nch" and any("AirSewa" in n and "could not be verified" in n for n in air.needs_check)


def test_card_data_never_reaches_the_portal_text():
    with pytest.raises(LetterError):
        build_kit(case(facts=[Fact(name="note", value="card 4111 1111 1111 1111")]), D0)


def test_api_portal_kit(tmp_path, monkeypatch):
    store = CaseStore(tmp_path / "c.json")
    store.save(case())
    app.dependency_overrides[tracked.get_store] = lambda: store
    monkeypatch.setattr(tracked, "_today", lambda: D0)
    try:
        cl = TestClient(app)
        r = cl.get("/tracked-cases/k1/portal-kit")
        assert r.status_code == 200 and r.json()["regulator_key"] == "nch" and r.json()["steps"][0]["source"]["quote"]
        assert cl.get("/tracked-cases/nope/portal-kit").status_code == 404
    finally:
        app.dependency_overrides.clear()
