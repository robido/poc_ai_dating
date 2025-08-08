import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from talkmatch.profile import ProfileStore
from talkmatch import readiness


class DummyAI:
    def __init__(self, response: str):
        self.response = response
        self.last_messages = None

    def get_response(self, messages):
        self.last_messages = messages
        return self.response


def test_is_ready_true(tmp_path, monkeypatch):
    ai = DummyAI("80")
    store = ProfileStore(base_dir=tmp_path)
    store.profiles["alice"] = "loves hiking"
    monkeypatch.setattr(readiness, "PROFILE_OBJECTIVES", ["hiking"])
    assert readiness.is_ready("alice", store, ai)
    prompt = ai.last_messages[0]["content"]
    assert "hiking" in prompt
    assert "loves hiking" in prompt


def test_is_ready_false(tmp_path, monkeypatch):
    ai = DummyAI("79")
    store = ProfileStore(base_dir=tmp_path)
    store.profiles["bob"] = "likes movies"
    monkeypatch.setattr(readiness, "PROFILE_OBJECTIVES", ["hiking"])
    assert not readiness.is_ready("bob", store, ai)
