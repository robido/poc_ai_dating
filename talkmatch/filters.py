from __future__ import annotations

"""User list filters for matchmaking."""

from typing import Protocol, List

from .ai import AIClient
from .profile import ProfileStore
from .readiness import ReadinessEvaluator, PROFILE_OBJECTIVES


class UserFilter(Protocol):
    """Filter a list of user names."""

    def filter(self, users: List[str]) -> List[str]:
        """Return a subset of ``users``."""


class ReadinessFilter(UserFilter):
    """Filter out users whose profiles are not ready."""

    def __init__(self, ai_client: AIClient, profile_store: ProfileStore) -> None:
        self.evaluator = ReadinessEvaluator(ai_client)
        self.profile_store = profile_store

    def filter(self, users: List[str]) -> List[str]:
        return [
            name
            for name in users
            if self.evaluator.is_ready(
                PROFILE_OBJECTIVES, self.profile_store.read(name)
            )
        ]
