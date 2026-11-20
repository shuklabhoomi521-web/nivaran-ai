"""Where tracked cases are kept. For now one JSON file (written atomically); the database comes with hosting.
The file holds private details, so it is git-ignored and must be encrypted before real users (see docs/notes/dpdp-basics.md)."""
import json
import os
from pathlib import Path

from app.cases.models import TrackedCase


class CaseStore:
    def __init__(self, path: str | os.PathLike):
        self.path = Path(path)

    def _read(self) -> dict[str, dict]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {}

    def _write(self, data: dict[str, dict]) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, self.path)

    def save(self, case: TrackedCase) -> None:
        data = self._read()
        data[case.id] = json.loads(case.model_dump_json())
        self._write(data)

    def get(self, case_id: str) -> TrackedCase | None:
        raw = self._read().get(case_id)
        return TrackedCase.model_validate(raw) if raw else None

    def list(self) -> list[TrackedCase]:
        return sorted((TrackedCase.model_validate(v) for v in self._read().values()), key=lambda c: (c.created_on, c.id))

    def delete(self, case_id: str) -> bool:
        """Remove a case completely (the user's delete-my-data right)."""
        data = self._read()
        if case_id not in data:
            return False
        del data[case_id]
        self._write(data)
        return True
