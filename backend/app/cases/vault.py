"""Encryption at rest for the files that hold private case details (cases and drafts).
Files are encrypted with a key from the environment (DATA_ENCRYPTION_KEY) or, if none is set, from a git-ignored key file created on first use.
A file that is still plain JSON from an earlier version is read once and rewritten encrypted."""
import json
import os
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_KEY_FILE = ROOT / ".data_key"


class VaultError(RuntimeError):
    pass


def _key(key_file: Path) -> bytes:
    env = os.getenv("DATA_ENCRYPTION_KEY", "").strip()
    if env:
        return env.encode()
    if not key_file.exists():
        key_file.write_bytes(Fernet.generate_key())
        key_file.chmod(0o600)
    return key_file.read_bytes().strip()


class Vault:
    def __init__(self, key_file: Path = DEFAULT_KEY_FILE):
        try:
            self._f = Fernet(_key(key_file))
        except (ValueError, TypeError) as e:
            raise VaultError("DATA_ENCRYPTION_KEY is not a valid key (make one with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\")") from e

    def read(self, path: Path) -> dict:
        try:
            raw = path.read_bytes()
        except FileNotFoundError:
            return {}
        if raw.lstrip()[:1] in (b"{", b"["):                   # an old plain file: accept it, the next write encrypts it
            return json.loads(raw.decode("utf-8"))
        try:
            return json.loads(self._f.decrypt(raw).decode("utf-8"))
        except InvalidToken as e:
            raise VaultError(f"{path.name} cannot be decrypted: wrong key, or the file is damaged") from e

    def write(self, path: Path, data: dict) -> None:
        tmp = path.with_suffix(".tmp")
        tmp.write_bytes(self._f.encrypt(json.dumps(data, ensure_ascii=False).encode("utf-8")))
        tmp.chmod(0o600)
        os.replace(tmp, path)
