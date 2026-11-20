import json

import pytest
from cryptography.fernet import Fernet

from app.cases.store import CaseStore
from app.cases.vault import Vault, VaultError
from app.letters.outbox import DraftStore
from tests.test_case_engine import contact, understood
from app.cases import engine
from app.cases.models import Rung
from datetime import date

D0 = date(2026, 12, 5)


def test_files_on_disk_are_not_readable_text(tmp_path):
    v = Vault(tmp_path / "key")
    s = CaseStore(tmp_path / "cases.json", v)
    c = engine.apply(engine.new_case(understood(), D0, "c1", user_name="Bhoomi Shukla"), contact(Rung.first_contact))
    s.save(c)
    raw = (tmp_path / "cases.json").read_bytes()
    assert b"Bhoomi" not in raw and b"4839201" not in raw and b"Swiggy" not in raw and raw.lstrip()[:1] not in (b"{", b"[")
    assert s.get("c1") == c                                              # still reads back exactly
    assert oct((tmp_path / "cases.json").stat().st_mode & 0o777) == "0o600"          # only the owner can open it
    assert oct((tmp_path / "key").stat().st_mode & 0o777) == "0o600"


def test_old_plain_file_is_read_once_then_rewritten_encrypted(tmp_path):
    v = Vault(tmp_path / "key")
    c = engine.new_case(understood(), D0, "c1", user_name="Bhoomi Shukla")
    (tmp_path / "cases.json").write_text(json.dumps({"c1": json.loads(c.model_dump_json())}))
    s = CaseStore(tmp_path / "cases.json", v)
    assert s.get("c1") == c
    s.save(engine.new_case(understood(), D0, "c2"))
    assert b"Bhoomi" not in (tmp_path / "cases.json").read_bytes()
    assert {x.id for x in s.list()} == {"c1", "c2"}


def test_wrong_key_is_an_error_not_silent_data_loss(tmp_path):
    CaseStore(tmp_path / "cases.json", Vault(tmp_path / "key1")).save(engine.new_case(understood(), D0, "c1"))
    with pytest.raises(VaultError):
        CaseStore(tmp_path / "cases.json", Vault(tmp_path / "key2")).list()


def test_key_from_the_environment_wins_and_a_bad_key_is_explained(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_ENCRYPTION_KEY", Fernet.generate_key().decode())
    Vault(tmp_path / "unused-key")
    assert not (tmp_path / "unused-key").exists()
    monkeypatch.setenv("DATA_ENCRYPTION_KEY", "not-a-key")
    with pytest.raises(VaultError):
        Vault(tmp_path / "k")


def test_drafts_are_encrypted_too(tmp_path):
    from tests.test_letters import draft_for, case
    d = draft_for(case())
    store = DraftStore(tmp_path / "d.json", Vault(tmp_path / "key"))
    store.save(d)
    raw = (tmp_path / "d.json").read_bytes()
    assert b"Order arrived cold" not in raw and b"grievances@swiggy.in" not in raw
    assert store.get(d.id) == d
