"""AI client wrapper for TalkMatch.

This module provides a thin wrapper around the OpenAI API so that
it can be easily mocked during testing.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Dict

from openai import OpenAI


@dataclass
class AIClient:
    """Simple wrapper around the OpenAI chat completion API."""

    api_key: str | None = None
    max_tokens: int = 150

    def __post_init__(self) -> None:
        key = self.api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY is not set")
        self.client = OpenAI(api_key=key)

    def get_response(self, messages: List[Dict[str, str]]) -> str:
        """Send messages to the OpenAI API and return the assistant reply."""
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=self.max_tokens,
        )
        return completion.choices[0].message.content
