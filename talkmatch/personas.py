from __future__ import annotations

"""Definitions for AI dating personas used in the demo."""

from dataclasses import dataclass
from typing import List

from .prompts import PERSONA_DESCRIPTIONS


@dataclass
class Persona:
    """Represents an AI-powered dating persona."""

    name: str
    description: str

    @property
    def system_prompt(self) -> str:
        return (
            f"You are {self.name}. {self.description} "
            "You're texting on a dating app and only half-interested. "
            "Use short lines, even one-word replies, with playful sarcasm. "
            "Only ask questions if you feel like it and occasionally send nothing at all. "
            "If you choose to send nothing, reply with an empty message and do not mention ghosting or placeholders. "
            "Keep it casual and unpredictable; let your interest shift with the vibe, attraction, excitement, or mood."
        )


def load_personas() -> List[Persona]:
    """Create Persona objects from the loaded descriptions."""
    personas: List[Persona] = []
    for name in sorted(PERSONA_DESCRIPTIONS):
        personas.append(Persona(name=name, description=PERSONA_DESCRIPTIONS[name]))
    return personas


PERSONAS = load_personas()
