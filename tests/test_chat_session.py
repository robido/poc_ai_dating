import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from talkmatch.chat import ChatSession, FakeUser
from talkmatch.profile import ProfileStore


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
    session = ChatSession(ai_client=DummyAI(["Stored profile", "AI reply"]), profile_store=store)
    reply = session.send_client_message("Alice", "Hello")
    assert reply == "AI reply"
    assert (tmp_path / "Alice.txt").read_text().strip() == "Stored profile"


def test_chat_session_switch_to_fake_user(tmp_path):
    store = ProfileStore(base_dir=tmp_path)
    session = ChatSession(ai_client=DummyAI(["Stored profile"]), profile_store=store)
    fake = FakeUser(["Hi I'm fake"])
    session.switch_to_fake_user(fake)
    reply = session.send_client_message("Bob", "Hello")
    assert reply == "Hi I'm fake"
    assert (tmp_path / "Bob.txt").read_text().strip() == "Stored profile"
