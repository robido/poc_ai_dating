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
    session = ChatSession(
        ai_client=DummyAI(["Stored profile", "AI reply"]),
        profile_store=store,
        history_path=tmp_path / "history.json",
    )
    reply = session.send_client_message("Alice", "Hello")
    assert reply == "AI reply"
    assert (tmp_path / "Alice.txt").read_text().strip() == "Stored profile"


def test_chat_session_switch_to_fake_user(tmp_path):
    store = ProfileStore(base_dir=tmp_path)
    session = ChatSession(
        ai_client=DummyAI(["Stored profile"]),
        profile_store=store,
        history_path=tmp_path / "history.json",
    )
    fake = FakeUser(["Hi I'm fake"])
    session.switch_to_fake_user(fake)
    reply = session.send_client_message("Bob", "Hello")
    assert reply == "Hi I'm fake"
    assert (tmp_path / "Bob.txt").read_text().strip() == "Stored profile"


def test_chat_session_tracks_persona_messages(tmp_path):
    store = ProfileStore(base_dir=tmp_path)
    (tmp_path / "Alex.txt").write_text("Profile", encoding="utf-8")
    session = ChatSession(
        ai_client=DummyAI(["Stored profile", "AI reply"]),
        profile_store=store,
        history_path=tmp_path / "history.json",
    )
    session.set_persona("Alex")
    reply = session.send_client_message("Alice", "Hi")
    assert reply == "AI reply"
    assert session.persona_message_counts["Alex"] == 1


def test_clear_matches_resets_persona(tmp_path):
    store = ProfileStore(base_dir=tmp_path)
    session = ChatSession(
        ai_client=DummyAI(["profile", "reply"]),
        profile_store=store,
        history_path=tmp_path / "history.json",
    )
    session.set_persona("Pat")
    session.persona_message_counts["Pat"] = 2
    session.clear_matches()
    assert session.matched_persona is None
    assert session.persona_message_counts == {}


def test_chat_session_persists_history(tmp_path):
    store = ProfileStore(base_dir=tmp_path)
    history = tmp_path / "history.json"
    session1 = ChatSession(
        ai_client=DummyAI(["profile1", "reply1"]),
        profile_store=store,
        history_path=history,
    )
    session1.send_client_message("Alice", "Hello")
    assert history.exists()

    session2 = ChatSession(
        ai_client=DummyAI(["profile2", "reply2"]),
        profile_store=store,
        history_path=history,
    )
    assert session2.messages[1]["content"] == "Hello"
