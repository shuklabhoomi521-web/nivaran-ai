import pytest
from fastapi.testclient import TestClient

from app.api.cases import get_llm
from app.main import app


class FakeLLM:
    """Stands in for Claude. Returns a canned answer and remembers what it was sent."""

    def __init__(self, answer: dict):
        self.answer = answer
        self.calls: list[dict] = []

    def complete_json(self, *, system: str, user: str, schema: dict) -> dict:
        self.calls.append({"system": system, "user": user, "schema": schema})
        return self.answer


def case_dict(**over) -> dict:
    base = {
        "company": "Swiggy",
        "category": "food_delivery",
        "category_confidence": "high",
        "problem_summary": "Order arrived cold; no refund.",
        "user_goal": "refund",
        "details_known": [{"name": "order_id", "value": "4839201"}],
        "details_missing": [],
        "user_language": "english",
        "urgency": "medium",
        "other_issues": [],
        "follow_up_question": None,
    }
    base.update(over)
    return base


@pytest.fixture
def client_with():
    """client_with(answer) -> (TestClient, FakeLLM) wired to a fake Claude."""

    def make(answer: dict):
        fake = FakeLLM(answer)
        app.dependency_overrides[get_llm] = lambda: fake
        return TestClient(app), fake

    yield make
    app.dependency_overrides.clear()
