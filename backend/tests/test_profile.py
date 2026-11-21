"""The person's own profile: validated, encrypted at rest, private to its owner."""
from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.api import profile as profile_api
from app.main import app
from app.profiles.store import ProfileStore
from app.users import add_user

GOOD = {"full_name": "Asha  Rao", "gender": "female", "date_of_birth": "2000-06-15", "phone": "+91 98765 43210", "email": "asha@example.com", "city": "Chennai", "preferred_language": "ta"}


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setenv("PILOT_USERS_FILE", str(tmp_path / "users.json"))
    monkeypatch.setenv("PROFILE_STORE_FILE", str(tmp_path / "profiles.json"))
    monkeypatch.setenv("DATA_ENCRYPTION_KEY", __import__("cryptography.fernet", fromlist=["Fernet"]).Fernet.generate_key().decode())
    monkeypatch.setenv("NIVARAN_API_TOKEN", "builder-secret-not-real")
    monkeypatch.setattr(profile_api, "_today", lambda: date(2026, 12, 5))
    _, t1 = add_user("A", tmp_path / "users.json")
    _, t2 = add_user("B", tmp_path / "users.json")
    c = TestClient(app, client=("192.168.1.9", 50000))
    h = lambda t: {"Authorization": f"Bearer {t}"}
    return c, h(t1), h(t2), tmp_path


def test_empty_then_save_then_read(env):
    c, a, _, _ = env
    assert c.get("/profile", headers=a).json() == {"profile": None}
    r = c.put("/profile", json=GOOD, headers=a)
    assert r.status_code == 200
    got = c.get("/profile", headers=a).json()["profile"]
    assert got["full_name"] == "Asha Rao" and got["phone"] == "+919876543210" and got["preferred_language"] == "ta"


def test_people_cannot_see_each_others_profile(env):
    c, a, b, _ = env
    c.put("/profile", json=GOOD, headers=a)
    assert c.get("/profile", headers=b).json() == {"profile": None}
    assert c.delete("/profile", headers=b).json() == {"deleted": False}
    assert c.get("/profile", headers=a).json()["profile"] is not None


def test_delete_my_profile(env):
    c, a, _, _ = env
    c.put("/profile", json=GOOD, headers=a)
    assert c.delete("/profile", headers=a).json() == {"deleted": True}
    assert c.get("/profile", headers=a).json() == {"profile": None}


def test_stored_encrypted_not_plain(env):
    c, a, _, tmp = env
    c.put("/profile", json=GOOD, headers=a)
    raw = (tmp / "profiles.json").read_bytes()
    assert b"Asha" not in raw and b"asha@example.com" not in raw and b"9876543210" not in raw


@pytest.mark.parametrize("change,fragment", [
    ({"date_of_birth": "2010-01-01"}, "18"),
    ({"date_of_birth": "2027-01-01"}, "future"),
    ({"gender": "robot"}, "gender"),
    ({"full_name": "   "}, "empty"),
    ({"phone": "12345"}, "phone"),
    ({"email": "not-an-email"}, "email"),
    ({"preferred_language": "fr"}, "language"),
    ({"extra_field": "x"}, "extra"),
])
def test_bad_input_is_refused_and_nothing_is_saved(env, change, fragment):
    c, a, _, _ = env
    r = c.put("/profile", json={**GOOD, **change}, headers=a)
    assert r.status_code == 422 and fragment in r.text
    assert c.get("/profile", headers=a).json() == {"profile": None}


def test_exactly_eighteen_today_is_allowed(env):
    c, a, _, _ = env
    assert c.put("/profile", json={**GOOD, "date_of_birth": "2008-12-05"}, headers=a).status_code == 200
    assert c.put("/profile", json={**GOOD, "date_of_birth": "2008-12-06"}, headers=a).status_code == 422


def test_needs_the_access_code(env):
    c, *_ = env
    assert c.get("/profile").status_code == 401
    assert c.put("/profile", json=GOOD).status_code == 401


def test_store_roundtrip_without_http(tmp_path, monkeypatch):
    from cryptography.fernet import Fernet
    from app.cases.vault import Vault
    from app.profiles.models import Profile
    st = ProfileStore(tmp_path / "p.json", Vault(tmp_path / "k"))
    st.save("u1", Profile(**GOOD))
    assert st.get("u1").city == "Chennai" and st.get("u2") is None


def test_browser_preflight_allows_put(env):
    c, *_ = env
    r = c.options("/profile", headers={"Origin": "http://localhost:8081", "Access-Control-Request-Method": "PUT", "Access-Control-Request-Headers": "authorization,content-type"})
    assert r.status_code == 200 and "PUT" in r.headers["access-control-allow-methods"]
