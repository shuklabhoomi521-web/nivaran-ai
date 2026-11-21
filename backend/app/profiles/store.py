"""One encrypted file holding every person's profile, keyed by user id (same vault as the cases)."""
import json
import os
from pathlib import Path

from app.cases.vault import Vault
from app.profiles.models import Profile


class ProfileStore:
    def __init__(self, path: str | os.PathLike, vault: Vault | None = None):
        self.path = Path(path)
        self.vault = vault or Vault()

    def get(self, user_id: str) -> Profile | None:
        raw = self.vault.read(self.path).get(user_id)
        return Profile.model_validate(raw) if raw else None

    def save(self, user_id: str, profile: Profile) -> None:
        data = self.vault.read(self.path)
        data[user_id] = json.loads(profile.model_dump_json())
        self.vault.write(self.path, data)

    def delete(self, user_id: str) -> bool:
        data = self.vault.read(self.path)
        if user_id not in data:
            return False
        del data[user_id]
        self.vault.write(self.path, data)
        return True
