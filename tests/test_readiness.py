import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from talkmatch.profile import ProfileStore
from talkmatch import readiness
from talkmatch import filters as user_filters


class DummyAI:
    def __init__(self, responses: list[str]):
        self.responses = responses
        self.last_messages = None

    def get_response(self, messages):
        self.last_messages = messages
        return self.responses.pop(0)


def test_is_ready_true(tmp_path, monkeypatch):
    ai = DummyAI(["80"])
    store = ProfileStore(base_dir=tmp_path)
    store.profiles["alice"] = "loves hiking"
    monkeypatch.setattr(readiness, "PROFILE_OBJECTIVES", ["hiking"])
    assert readiness.is_ready("alice", store, ai)
    prompt = ai.last_messages[0]["content"]
    assert "hiking" in prompt
    assert "loves hiking" in prompt


def test_is_ready_false(tmp_path, monkeypatch):
    ai = DummyAI(["79"])
    store = ProfileStore(base_dir=tmp_path)
    store.profiles["bob"] = "likes movies"
    monkeypatch.setattr(readiness, "PROFILE_OBJECTIVES", ["hiking"])
    assert not readiness.is_ready("bob", store, ai)


def test_readiness_filter_filters_users(tmp_path, monkeypatch):
    store = ProfileStore(base_dir=tmp_path)
    store.profiles["alice"] = "hiking"
    store.profiles["bob"] = "movies"
    monkeypatch.setattr(user_filters, "PROFILE_OBJECTIVES", ["hiking"])
    filt = user_filters.ReadinessFilter(DummyAI(["80", "79"]), store)
    assert filt.filter(["alice", "bob"]) == ["alice"]
