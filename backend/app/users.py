"""The people allowed to use this server. One entry per person: an id, a label and the SHA-256 of their secret token (the token itself is shown once
when the person is added and is never stored). The file is git-ignored.
Id "owner" is the builder: it also owns every case made before accounts existed, and it is the only id allowed to place calls."""
import hashlib
import hmac
import json
import os
import secrets
from pathlib import Path

LEGACY_OWNER = "owner"
DEFAULT_FILE = Path(__file__).resolve().parents[2] / ".pilot_users.json"
_cache: dict = {"path": None, "mtime": None, "users": []}


def users_file() -> Path:
    return Path(os.getenv("PILOT_USERS_FILE", str(DEFAULT_FILE)))


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def load_users(path: Path | None = None) -> list[dict]:
    p = path or users_file()
    try:
        mtime = p.stat().st_mtime_ns
    except FileNotFoundError:
        return []
    if _cache["path"] == str(p) and _cache["mtime"] == mtime:
        return _cache["users"]
    users = json.loads(p.read_text(encoding="utf-8")).get("users", [])
    _cache.update(path=str(p), mtime=mtime, users=users)
    return users


def find_user(token: str, path: Path | None = None) -> str | None:
    """The user id for a token, or None. Constant-time comparison."""
    h = hash_token(token)
    found = None
    for u in load_users(path):
        if hmac.compare_digest(u["token_sha256"], h):
            found = u["id"]
    return found


def _save(path: Path, users: list[dict]) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"users": users}, indent=2), encoding="utf-8")
    tmp.chmod(0o600)
    os.replace(tmp, path)
    _cache["mtime"] = None


def add_user(label: str, path: Path | None = None, user_id: str | None = None) -> tuple[str, str]:
    """Returns (user id, token). The token is returned once; only its hash is kept."""
    p = path or users_file()
    users = list(load_users(p))
    uid = user_id or f"u{len(users) + 1}"
    if any(u["id"] == uid for u in users):
        raise ValueError(f"id {uid} already exists")
    token = secrets.token_urlsafe(24)
    users.append({"id": uid, "label": label, "token_sha256": hash_token(token)})
    _save(p, users)
    return uid, token


def revoke_user(uid: str, path: Path | None = None) -> bool:
    p = path or users_file()
    users = list(load_users(p))
    kept = [u for u in users if u["id"] != uid]
    if len(kept) == len(users):
        return False
    _save(p, kept)
    return True
