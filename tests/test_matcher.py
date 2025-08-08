from __future__ import annotations

"""Tests for the AI-based matcher."""

from talkmatch.matcher import Matcher, build_prompt, _parse_score


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


def test_match_matrix_persistence(tmp_path):
    path = tmp_path / "matrix.json"
    users = ["A", "B"]
    matcher = Matcher(users, path=path)
    ai = DummyAI(["0.5"])
    store = DummyStore({"A": "profile a", "B": "profile b"})
    matcher.calculate(ai, profile_store=store)

    # Instantiate a new matcher using the persisted data
    matcher_loaded = Matcher(users, path=path)
    assert matcher_loaded.top_matches("A") == [("B", 0.5)]


def test_clear_resets_scores():
    users = ["A", "B"]
    matcher = Matcher(users)
    matcher.matrix["A"]["B"] = 0.8
    matcher.matrix["B"]["A"] = 0.8
    matcher.clear()
    assert matcher.matrix["A"]["B"] == 0.0
    assert matcher.matrix["B"]["A"] == 0.0


def test_build_prompt_and_parse_score_helpers():
    profiles = {"A": "profile a", "B": ""}
    prompt = build_prompt("A", "B", profiles)
    assert "profile a" in prompt
    assert "No information." in prompt
    assert _parse_score("0.75") == 0.75
    assert _parse_score("score: 1.0") == 1.0
    assert _parse_score("not a score") == 0.0
