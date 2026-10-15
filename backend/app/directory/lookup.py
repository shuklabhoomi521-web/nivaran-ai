import re

from app.directory.loader import load_companies
from app.directory.models import Company


def _norm(s: str) -> str:
    return re.sub(r"[\W_]+", "", s.casefold())


def find_company(name: str | None) -> Company | None:
    """Match a company name (any spelling, case, or listed alias) to a directory entry."""
    if not name or not _norm(name):
        return None
    wanted = _norm(name)
    for c in load_companies():
        if wanted in {_norm(c.name), *(_norm(a) for a in c.aliases)}:
            return c
    return None
