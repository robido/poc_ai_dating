import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from talkmatch.chat import ChatSession
from talkmatch.fake_user import FakeUser
from talkmatch.profile import ProfileStore
from talkmatch.storage import ChatStore


class DummyAI:
    def __init__(self, responses):
        self.responses = responses
        self.index = 0

    def get_response(self, messages):
        resp = self.responses[self.index]
        self.index += 1
        return resp


def test_chat_session_uses_ai(tmp_path):
    store = ProfileStore(base_dir=tmp_path)
    session = ChatSession(
        ai_client=DummyAI(["Stored profile", "AI reply"]),
        profile_store=store,
        chat_store=ChatStore(path=tmp_path / "history.json"),
    )
    reply = session.send_client_message("Alice", "Hello")
    assert reply == "AI reply"
    assert store.read("Alice") == "Stored profile"


def test_chat_session_switch_to_fake_user(tmp_path):
    store = ProfileStore(base_dir=tmp_path)
    session = ChatSession(
        ai_client=DummyAI(["Stored profile"]),
        profile_store=store,
        chat_store=ChatStore(path=tmp_path / "history.json"),
    )
    fake = FakeUser(["Hi I'm fake"])
    session.switch_to_fake_user(fake)
    reply = session.send_client_message("Bob", "Hello")
    assert reply == "Hi I'm fake"
    assert store.read("Bob") == "Stored profile"


def test_chat_session_persists_history(tmp_path):
    store = ProfileStore(base_dir=tmp_path)
    history = tmp_path / "history.json"
    session1 = ChatSession(
        ai_client=DummyAI(["profile1", "reply1"]),
        profile_store=store,
        chat_store=ChatStore(path=history),
    )
    session1.send_client_message("Alice", "Hello")
    assert history.exists()

    session2 = ChatSession(
        ai_client=DummyAI(["profile2", "reply2"]),
        profile_store=store,
        chat_store=ChatStore(path=history),
    )
    assert session2.messages[1]["content"] == "Hello"
