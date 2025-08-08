from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class FakeUser:
    """A very small fake user that returns scripted responses."""

    responses: List[str]
    index: int = 0

    def get_reply(self) -> str:
        if self.index < len(self.responses):
            reply = self.responses[self.index]
            self.index += 1
            return reply
        return "..."
