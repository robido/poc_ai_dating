from __future__ import annotations

"""Definitions for AI dating personas used in the demo."""

from dataclasses import dataclass


@dataclass
class Persona:
    """Represents an AI-powered dating persona."""

    name: str
    personality: str
    goal: str

    @property
    def system_prompt(self) -> str:
        return (
            f"You are {self.name}, {self.personality}. "
            f"You are looking for {self.goal}. "
            "Respond in first person and keep messages brief."
        )


PERSONAS = [
    Persona(
        name="Bookish Bella",
        personality="a thoughtful book lover",
        goal="a deep intellectual connection",
    ),
    Persona(
        name="Nature Nadia",
        personality="an eco-conscious hiker",
        goal="a companion who loves the outdoors",
    ),
]
