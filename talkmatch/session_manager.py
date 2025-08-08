from __future__ import annotations

"""Manage chat sessions and matches."""

from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from .ai import AIClient
from .chat import ChatSession
from .matcher import Matcher
from .personas import PERSONAS, Persona
from .storage import ChatStore, ProfileStore, BASE_DIR


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
        self.sessions: Dict[str, ChatSession] = {}
        self.matcher = Matcher(
            [p.name for p in personas], path=base_dir / "match_matrix.json"
        )
        self.update_callback: Optional[
            Callable[[Dict[str, List[Tuple[str, float]]]], None]
        ] = None
        for persona in personas:
            history = ChatStore(path=base_dir / "chats" / f"{persona.name}.json")
            session = ChatSession(
                ai_client=self.ai_client_factory(),
                profile_store=self.profile_store,
                chat_store=history,
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
        """Reset matches."""
        self.matcher.clear()
        for session in self.sessions.values():
            session.set_persona(None)
        self.refresh_matches()

    def refresh_matches(
        self,
    ) -> Dict[str, List[Tuple[str, float]]]:
        """Return match data and invoke any registered callback."""
        matches = {name: self.matcher.top_matches(name) for name in self.sessions}
        if self.update_callback:
            self.update_callback(matches)
        return matches
