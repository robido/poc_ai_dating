"""Chat session logic for TalkMatch."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional

from .ai import AIClient
from .profile import ProfileStore

# Load the ambassador role description from a text file to keep the code tidy.
AMBASSADOR_ROLE = Path(__file__).with_name("ambassador_role.txt").read_text().strip()

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
        default_factory=lambda: [{"role": "system", "content": AMBASSADOR_ROLE}]
    )
    fake_user: Optional[FakeUser] = None
    matched_persona: Optional[str] = None
    persona_message_counts: Dict[str, int] = field(default_factory=dict)

    def send_client_message(self, name: str, text: str) -> str:
        """Handle a message from any client (user or persona)."""

        self.messages.append({"role": "user", "content": text})
        self.profile_store.update(self.ai_client, name, text)
        if self.fake_user:
            reply = self.fake_user.get_reply()
        else:
            messages = self.messages
            if self.matched_persona:
                profile = self.profile_store.read(self.matched_persona)
                persona_prompt = (
                    f"Act as {self.matched_persona} using this profile: {profile}. "
                    "Maintain the current topic and shift gradually from the ambassador's tone to "
                    f"{self.matched_persona}'s style."
                )
                messages = messages + [{"role": "system", "content": persona_prompt}]
            reply = self.ai_client.get_response(messages)
        self.messages.append({"role": "assistant", "content": reply})
        if self.matched_persona:
            self.persona_message_counts[self.matched_persona] = (
                self.persona_message_counts.get(self.matched_persona, 0) + 1
            )
        return reply

    def switch_to_fake_user(self, fake_user: FakeUser) -> None:
        self.fake_user = fake_user

    def set_persona(self, persona: Optional[str]) -> None:
        """Switch the ambassador to act as a given persona."""
        self.matched_persona = persona
