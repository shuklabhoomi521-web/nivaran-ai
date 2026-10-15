import json
from functools import lru_cache
from pathlib import Path

from app.directory.models import Company

DATA_FILE = Path(__file__).resolve().parent / "companies.json"


@lru_cache
def load_companies() -> tuple[Company, ...]:
    raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return tuple(Company.model_validate(c) for c in raw)
