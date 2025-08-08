"""Chat session logic for TalkMatch."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable

from .ai import AIClient
from .storage import ProfileStore, ChatStore
from .fake_user import FakeUser
from .prompts import AMBASSADOR_ROLE, COLLECT_INFO_PROMPT
from .objectives import PROFILE_OBJECTIVES
from .ambassador import Ambassador


AMBASSADOR_SYSTEM_PROMPT = (
    AMBASSADOR_ROLE
    + "\n"
    + COLLECT_INFO_PROMPT.replace("{objectives}", ", ".join(PROFILE_OBJECTIVES))
)



@dataclass
class ChatSession:
    """Manages conversation state and talks to the AI or a fake user."""

    ai_client: AIClient
    profile_store: ProfileStore = field(default_factory=ProfileStore)
    chat_store: ChatStore | None = None
    messages: List[Dict[str, str]] = field(
        default_factory=lambda: [
            {"role": "system", "content": AMBASSADOR_SYSTEM_PROMPT}
        ]
    )
    fake_user: Optional[FakeUser] = None
    ambassador: Ambassador = field(default_factory=Ambassador)
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
        elif self.ambassador.state == "linked":
            reply = text
        else:
            messages = self.messages
            if self.ambassador.state == "acting" and self.ambassador.persona:
                profile = self.profile_store.read(self.ambassador.persona)
                persona_prompt = (
                    f"Act as {self.ambassador.persona} using this profile: {profile}. "
                    "Maintain the current topic and shift gradually from the ambassador's tone to "
                    f"{self.ambassador.persona}'s style."
                )
                messages = messages + [{"role": "system", "content": persona_prompt}]
            elif self.ambassador.state == "linking" and self.ambassador.link_context:
                link_prompt = (
                    f"Other user recently said: {self.ambassador.link_context}"
                )
                messages = messages + [{"role": "system", "content": link_prompt}]
            else:
                profile = self.profile_store.read(name).lower()
                outstanding = [
                    obj for obj in PROFILE_OBJECTIVES if obj.lower() not in profile
                ]
                if outstanding:
                    info_prompt = COLLECT_INFO_PROMPT.replace(
                        "{objectives}", ", ".join(outstanding)
                    )
                    messages = messages + [
                        {"role": "system", "content": info_prompt}
                    ]
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

    def ambassador_label(self) -> str:
        return f"Ambassador [{self.ambassador.status()}]"

    def set_persona(self, persona: Optional[str]) -> None:
        """Switch the ambassador to act as a given persona."""
        self.ambassador.set_persona(persona)
