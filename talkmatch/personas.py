from __future__ import annotations

"""Definitions for AI dating personas used in the demo."""

from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class Persona:
    """Represents an AI-powered dating persona."""

    name: str
    description: str

    @property
    def system_prompt(self) -> str:
        return (
            f"You are {self.name}. {self.description} "
            "Respond in first person with casual, natural language. "
            "Keep replies to at most three sentences and it's fine to be a bit informal or make small mistakes."
        )


def load_personas() -> List[Persona]:
    """Load persona descriptions from text files."""
    base = Path(__file__).with_name("persona_descriptions")
    personas: List[Persona] = []
    for path in sorted(base.glob("*.txt")):
        personas.append(Persona(name=path.stem, description=path.read_text().strip()))
    return personas


PERSONAS = load_personas()
