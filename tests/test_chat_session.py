import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from talkmatch.chat import ChatSession, FakeUser


class DummyAI:
    def get_response(self, messages):
        return "AI reply"


def test_chat_session_uses_ai():
    session = ChatSession(ai_client=DummyAI())
    reply = session.send_user_message("Hello")
    assert reply == "AI reply"


def test_chat_session_switch_to_fake_user():
    session = ChatSession(ai_client=DummyAI())
    fake = FakeUser(["Hi I'm fake"])
    session.switch_to_fake_user(fake)
    reply = session.send_user_message("Hello")
    assert reply == "Hi I'm fake"
