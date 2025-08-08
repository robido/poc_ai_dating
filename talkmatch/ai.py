"""AI client wrapper for TalkMatch.

This module provides a thin wrapper around the OpenAI API so that
it can be easily mocked during testing.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Dict, Any

from openai import OpenAI


@dataclass
class AIClient:
    """Simple wrapper around the OpenAI chat completion API."""

    api_key: str | None = None
    # Allow larger responses so profiles are not truncated.
    max_tokens: int = 500
    # Optional preconfigured OpenAI client for dependency injection.
    openai_client: Any | None = None

    def __post_init__(self) -> None:
        if self.openai_client is not None:
            # Use the provided client directly.
            self.client = self.openai_client
            return

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
