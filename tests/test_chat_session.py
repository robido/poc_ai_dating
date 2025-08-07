import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from talkmatch.chat import ChatSession, FakeUser
from talkmatch.profile import ProfileStore


class DummyAI:
    def get_response(self, messages):
        return "AI reply"


def test_chat_session_uses_ai(tmp_path):
    store = ProfileStore(base_dir=tmp_path)
    session = ChatSession(ai_client=DummyAI(), profile_store=store)
    reply = session.send_client_message("Alice", "Hello")
    assert reply == "AI reply"
    assert (tmp_path / "Alice.txt").read_text().strip() == "Hello"


def test_chat_session_switch_to_fake_user(tmp_path):
    store = ProfileStore(base_dir=tmp_path)
    session = ChatSession(ai_client=DummyAI(), profile_store=store)
    fake = FakeUser(["Hi I'm fake"])
    session.switch_to_fake_user(fake)
    reply = session.send_client_message("Bob", "Hello")
    assert reply == "Hi I'm fake"
    assert (tmp_path / "Bob.txt").read_text().strip() == "Hello"
