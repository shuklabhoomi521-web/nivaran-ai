"""Which regulator or portal a complaint should go to, by company category. Data lives in regulators.json (official page and exact quote each)."""
import json
from functools import lru_cache
from pathlib import Path

from app.directory.models import Regulator
from app.models.case import Category

DATA_FILE = Path(__file__).resolve().parent / "regulators.json"
FALLBACK_KEY = "nch"   # the National Consumer Helpline takes any consumer grievance


@lru_cache
def load_regulators() -> tuple[Regulator, ...]:
    return tuple(Regulator.model_validate(r) for r in json.loads(DATA_FILE.read_text(encoding="utf-8")))


def regulator_for(category: Category) -> Regulator:
    """The regulator that covers this category. A regulator we could not verify is skipped in favour of the helpline."""
    regs = load_regulators()
    for r in regs:
        if category in r.covers and r.source is not None:
            return r
    return next(r for r in regs if r.key == FALLBACK_KEY)
