"""Chat session logic for TalkMatch."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from .ai import AIClient
from .profile import ProfileStore

AMBASSADOR_ROLE = ("You are the ambassador, an AI that chats with people on a dating app, and the goal is to role play a "
                   "human while trying to get to know the person. As you chat, you get a feel for their personality, "
                   "talking style, needs and the more you know the better we can than match them.")

@dataclass
class FakeUser:
    """A very small fake user that returns scripted responses."""

    responses: List[str]
    index: int = 0

    def get_reply(self) -> str:
        if self.index < len(self.responses):
            reply = self.responses[self.index]
            self.index += 1
            return reply
        return "..."


@dataclass
class ChatSession:
    """Manages conversation state and talks to the AI or a fake user."""

    ai_client: AIClient
    profile_store: ProfileStore = field(default_factory=ProfileStore)
    messages: List[Dict[str, str]] = field(
        default_factory=lambda: [
            {"role": "system", "content": "You are TalkMatch, an AI dating assistant."}
        ]
    )
    fake_user: Optional[FakeUser] = None

    def send_client_message(self, name: str, text: str) -> str:
        """Handle a message from any client (user or persona)."""

        self.messages.append({"role": "user", "content": text})
        self.profile_store.append(name, text)
        if self.fake_user:
            reply = self.fake_user.get_reply()
        else:
            reply = self.ai_client.get_response(self.messages)
        self.messages.append({"role": "assistant", "content": reply})
        return reply

    def switch_to_fake_user(self, fake_user: FakeUser) -> None:
        self.fake_user = fake_user
