from __future__ import annotations

"""Manage chat sessions, matches, and message counts."""

from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from .ai import AIClient
from .chat import ChatSession
from .matcher import Matcher
from .personas import PERSONAS, Persona
from .storage import ChatStore, MessageCountStore, ProfileStore, BASE_DIR


class SessionManager:
    """Handle persona sessions and matchmaking independent of the GUI."""

    def __init__(
        self,
        personas: List[Persona] = PERSONAS,
        base_dir: Path = BASE_DIR,
        ai_client_factory: Callable[[], AIClient] = AIClient,
    ) -> None:
        self.personas = personas
        self.base_dir = base_dir
        self.ai_client_factory = ai_client_factory
        self.profile_store = ProfileStore(base_dir=base_dir / "profiles")
        self.message_counts = MessageCountStore(path=base_dir / "message_counts.json")
        self.sessions: Dict[str, ChatSession] = {}
        self.matcher = Matcher(
            [p.name for p in personas], path=base_dir / "match_matrix.json"
        )
        self.update_callback: Optional[
            Callable[[Dict[str, List[Tuple[str, float]]], Dict[Tuple[str, str], int]], None]
        ] = None
        for persona in personas:
            history = ChatStore(path=base_dir / "chats" / f"{persona.name}.json")
            session = ChatSession(
                ai_client=self.ai_client_factory(),
                profile_store=self.profile_store,
                chat_store=history,
                message_counts=self.message_counts,
            )
            session.update_callback = self.refresh_matches
            self.sessions[persona.name] = session

    # Public API ---------------------------------------------------------
    def calculate(self) -> None:
        """Compute matches and assign personas to sessions."""
        ai = self.ai_client_factory()
        self.matcher.calculate(ai, profile_store=self.profile_store)
        for persona in self.personas:
            top = self.matcher.top_matches(persona.name, 1)
            session = self.sessions[persona.name]
            if top and top[0][1] > 0:
                session.set_persona(top[0][0])
            else:
                session.set_persona(None)
        self.refresh_matches()

    def clear(self) -> None:
        """Reset matches and message counts."""
        self.matcher.clear()
        for session in self.sessions.values():
            session.set_persona(None)
        self.message_counts.clear()
        self.refresh_matches()

    def refresh_matches(
        self,
    ) -> Tuple[Dict[str, List[Tuple[str, float]]], Dict[Tuple[str, str], int]]:
        """Return match data and invoke any registered callback."""
        matches = {name: self.matcher.top_matches(name) for name in self.sessions}
        counts = self.message_counts.counts
        if self.update_callback:
            self.update_callback(matches, counts)
        return matches, counts
