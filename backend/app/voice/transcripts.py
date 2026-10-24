"""Call transcripts: text only (never audio), stored ENCRYPTED on disk. The key lives in a git-ignored file (.transcript_key)."""
import json
import re
import time
from pathlib import Path

from cryptography.fernet import Fernet

from app.safety.redact import scrub

ROOT = Path(__file__).resolve().parents[3]
KEY_FILE = ROOT / ".transcript_key"
DIR = ROOT / ".call_transcripts"


def _fernet(key_file: Path = KEY_FILE) -> Fernet:
    if not key_file.exists():
        key_file.write_bytes(Fernet.generate_key())
        key_file.chmod(0o600)
    return Fernet(key_file.read_bytes())


def save(call_id: str, turns: list[dict], directory: Path = DIR, key_file: Path = KEY_FILE) -> Path:
    """turns: [{"who": "agent"|"ai"|"system", "text": ..., "t": seconds_since_start}]. Secrets are removed before saving."""
    clean = [{**t, "text": scrub({"t": t["text"]})[0]["t"]} for t in turns]
    directory.mkdir(exist_ok=True)
    path = directory / (re.sub(r"[^A-Za-z0-9_-]", "", call_id) + ".bin")
    path.write_bytes(_fernet(key_file).encrypt(json.dumps({"saved": time.strftime("%Y-%m-%d %H:%M:%S"), "turns": clean}, ensure_ascii=False).encode()))
    path.chmod(0o600)
    return path


def load(call_id: str, directory: Path = DIR, key_file: Path = KEY_FILE) -> dict:
    path = directory / (re.sub(r"[^A-Za-z0-9_-]", "", call_id) + ".bin")
    return json.loads(_fernet(key_file).decrypt(path.read_bytes()))
