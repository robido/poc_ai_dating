"""Chat session logic for TalkMatch."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable

from .ai import AIClient
from .storage import ProfileStore, ChatStore
from .fake_user import FakeUser
from .prompts import AMBASSADOR_ROLE



@dataclass
class ChatSession:
    """Manages conversation state and talks to the AI or a fake user."""

    ai_client: AIClient
    profile_store: ProfileStore = field(default_factory=ProfileStore)
    chat_store: ChatStore | None = None
    messages: List[Dict[str, str]] = field(
        default_factory=lambda: [{"role": "system", "content": AMBASSADOR_ROLE}]
    )
    fake_user: Optional[FakeUser] = None
    matched_persona: Optional[str] = None
    ambassador_status: str = field(init=False, default="")
    update_callback: Optional[Callable[[], None]] = None

    def __post_init__(self) -> None:
        if self.chat_store:
            loaded = self.chat_store.load()
            if loaded:
                self.messages = loaded
        self.set_persona(None)

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
        self.save_history()
        if self.update_callback:
            self.update_callback()
        return reply

    def save_history(self) -> None:
        if self.chat_store:
            self.chat_store.save(self.messages)

    def switch_to_fake_user(self, fake_user: FakeUser) -> None:
        self.fake_user = fake_user

    def set_status(self, status: str) -> None:
        """Update the ambassador's activity label."""
        self.ambassador_status = status

    def ambassador_label(self) -> str:
        return f"Ambassador [{self.ambassador_status}]"

    def set_persona(self, persona: Optional[str]) -> None:
        """Switch the ambassador to act as a given persona."""
        self.matched_persona = persona
        if persona:
            self.set_status(f"acting as {persona}")
        else:
            self.set_status("collecting info")
