from __future__ import annotations

"""Tests for the AI-based matcher."""

from talkmatch.matcher import Matcher


class DummyAI:
    """Return predetermined responses for each compatibility query."""

    def __init__(self, responses: list[str]):
        self.responses = responses

    def get_response(self, messages):
        return self.responses.pop(0)


class DummyStore:
    """Minimal profile store used for testing."""

    def __init__(self, profiles):
        self.profiles = profiles

    def read(self, user: str) -> str:
        return self.profiles.get(user, "")


def test_top_matches_use_ai_scores():
    users = ["A", "B", "C"]
    matcher = Matcher(users)

    ai = DummyAI(["0.9", "0.6", "0.3"])
    store = DummyStore({"A": "profile a", "B": "profile b", "C": "profile c"})

    matcher.calculate(ai, profile_store=store)

    assert matcher.top_matches("A", top_n=2) == [("B", 0.9), ("C", 0.6)]
    assert matcher.top_matches("B", top_n=2) == [("A", 0.9), ("C", 0.3)]
