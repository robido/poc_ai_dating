import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from talkmatch.profile import ProfileStore


class CaptureAI:
    def __init__(self, responses):
        self.responses = responses
        self.index = 0
        self.last_messages = None

    def get_response(self, messages):
        self.last_messages = messages
        resp = self.responses[self.index]
        self.index += 1
        return resp


def test_profile_store_uses_message_placeholder(tmp_path):
    ai = CaptureAI(
        ["<USER_INFO>existing profile</USER_INFO>", "<USER_INFO>updated profile</USER_INFO>"]
    )
    store = ProfileStore(base_dir=tmp_path)
    store.update(ai, "user", "first message")
    store.update(ai, "user", "second message")
    prompt = ai.last_messages[0]["content"]
    assert "<USER_INFO>existing profile</USER_INFO>" in prompt
    assert "<CHAT_MESSAGES>second message</CHAT_MESSAGES>" in prompt
