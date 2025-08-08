from __future__ import annotations

"""Manage chat sessions and matches."""

from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from .ai import AIClient
from .chat import ChatSession
from .matcher import Matcher
from .personas import PERSONAS, Persona
from .storage import ChatStore, ProfileStore, BASE_DIR
from .filters import UserFilter, ReadinessFilter


class SessionManager:
    """Handle persona sessions and matchmaking independent of the GUI."""

    def __init__(
        self,
        personas: List[Persona] = PERSONAS,
        base_dir: Path = BASE_DIR,
        ai_client_factory: Callable[[], AIClient] = AIClient,
        filters: Optional[List[UserFilter]] = None,
        link_threshold: int = 2,
    ) -> None:
        self.personas = personas
        self.base_dir = base_dir
        self.ai_client_factory = ai_client_factory
        self.profile_store = ProfileStore(base_dir=base_dir / "profiles")
        if filters is None:
            readiness = ReadinessFilter(self.ai_client_factory(), self.profile_store)
            self.filters = [readiness]
        else:
            self.filters = filters
        self.sessions: Dict[str, ChatSession] = {}
        self.link_threshold = link_threshold
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
        users = [p.name for p in self.personas]
        for user_filter in self.filters:
            users = user_filter.filter(users)
        ai = self.ai_client_factory()
        self.matcher.calculate(ai, profile_store=self.profile_store, users=users)
        for persona in self.personas:
            session = self.sessions[persona.name]
            if persona.name not in users or self._has_official_match(persona.name):
                session.set_persona(None)
                continue
            top = [
                m
                for m in self.matcher.top_matches(persona.name, 1)
                if m[0] in users and self.matcher.matrix[persona.name].get(m[0], 0.0) < 1.0
            ]
            if top and top[0][1] > 0.5:
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

    # Linking and matching ------------------------------------------------
    def _user_messages(self, session: ChatSession) -> List[str]:
        return [m["content"] for m in session.messages if m["role"] == "user"]

    def _last_user_message(self, session: ChatSession) -> str:
        for msg in reversed(session.messages):
            if msg["role"] == "user":
                return msg["content"]
        return ""

    def _maybe_link(self, name: str) -> None:
        session = self.sessions[name]
        persona = session.ambassador.persona
        if not persona:
            return
        other = self.sessions.get(persona)
        if not other or other.ambassador.persona != name:
            return
        if (
            len(self._user_messages(session)) >= self.link_threshold
            and len(self._user_messages(other)) >= self.link_threshold
        ):
            context_a = self._last_user_message(other)
            context_b = self._last_user_message(session)
            session.ambassador.begin_link(persona, context_a)
            other.ambassador.begin_link(name, context_b)
            self._maybe_finalize_link(name)

    def _maybe_finalize_link(self, name: str) -> None:
        session = self.sessions[name]
        if session.ambassador.state != "linking":
            return
        other_name = session.ambassador.link_target
        if not other_name:
            return
        other = self.sessions[other_name]
        if other.ambassador.state != "linking" or other.ambassador.link_target != name:
            return
        if self._last_user_message(session).lower() == self._last_user_message(other).lower():
            session.ambassador.finalize_link()
            other.ambassador.finalize_link()

    def send_message(self, name: str, text: str) -> str:
        reply = self.sessions[name].send_client_message(name, text)
        self._maybe_link(name)
        self._maybe_finalize_link(name)
        return reply

    def declare_match(self, a: str, b: str) -> None:
        self.sessions[a].ambassador.declare_match(b)
        self.sessions[b].ambassador.declare_match(a)
        self.matcher.declare_official_match(a, b)

    def _has_official_match(self, user: str) -> bool:
        return any(score >= 1.0 for score in self.matcher.matrix.get(user, {}).values())
