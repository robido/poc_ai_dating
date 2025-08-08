from __future__ import annotations

"""Ambassador state machine for chat sessions."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Ambassador:
    """Handle ambassador states and labels."""

    state: str = "collecting_info"
    persona: Optional[str] = None
    link_target: Optional[str] = None
    link_context: Optional[str] = None

    def set_persona(self, persona: Optional[str]) -> None:
        """Switch to acting as ``persona`` or reset to collecting info."""
        self.persona = persona
        self.link_target = None
        self.link_context = None
        if persona:
            self.state = "acting"
        else:
            self.state = "collecting_info"

    def begin_link(self, other: str, context: str) -> None:
        """Enter linking mode with ``other`` using their recent context."""
        self.link_target = other
        self.link_context = context
        self.state = "linking"

    def finalize_link(self) -> None:
        """Move to linked mode once conversations converge."""
        self.state = "linked"

    def declare_match(self, other: str) -> None:
        """Record that an official match has occurred with ``other``."""
        self.link_target = other
        self.state = "matched"

    def status(self) -> str:
        """Return a descriptive label for the current state."""
        if self.state == "acting" and self.persona:
            return f"acting as {self.persona}"
        if self.state == "linking" and self.link_target:
            return f"trying to link with {self.link_target}"
        if self.state == "linked" and self.link_target:
            return f"linked with {self.link_target}"
        if self.state == "matched" and self.link_target:
            return f"matched with {self.link_target}"
        return "collecting info"
