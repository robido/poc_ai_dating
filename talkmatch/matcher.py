from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple
import re

from .ai import AIClient
from .storage import ProfileStore, MatchMatrixStore

_SCORE_RE = re.compile(r"0(?:\.\d+)?|1(?:\.0+)?")


def build_prompt(user_a: str, user_b: str, profiles: Dict[str, str]) -> str:
    """Construct the compatibility prompt for two users."""
    profile_a = profiles.get(user_a, "") or "No information."
    profile_b = profiles.get(user_b, "") or "No information."
    return (
        "Rate the romantic compatibility of the two people on a scale from 0 to 1.\n"
        f"Person A profile:\n{profile_a}\n"
        f"Person B profile:\n{profile_b}\n"
        "Respond with only the numeric score."
    )


def _parse_score(reply: str) -> float:
    """Extract a numeric score from the AI reply."""
    match = _SCORE_RE.search(reply)
    return float(match.group()) if match else 0.0


@dataclass
class Matcher:
    """Compute and store match scores between users."""

    users: List[str]
    path: Path | None = None
    matrix: Dict[str, Dict[str, float]] = field(init=False)
    store: MatchMatrixStore = field(init=False)

    def __post_init__(self) -> None:
        self.store = MatchMatrixStore(self.path) if self.path else MatchMatrixStore()
        self.matrix = self.store.load(self.users)

    def _save(self) -> None:
        self.store.save(self.matrix)

    def clear(self) -> None:
        """Reset all match scores to zero and persist the empty matrix."""
        self.matrix = {u: {v: 0.0 for v in self.users if v != u} for u in self.users}
        self._save()

    def calculate(
        self,
        ai_client: AIClient,
        profile_store: ProfileStore | None = None,
        users: List[str] | None = None,
    ) -> None:
        """Ask the AI to rate compatibility for each user pair.

        ``users`` may restrict the calculation to a subset of ``self.users``.
        The AI is prompted with the stored profiles of each pair of users and
        expected to return a floating point number between 0 and 1.  The score
        is stored symmetrically in the matrix.  Because our demo only has a
        handful of users we simply perform one request per pair.
        """

        target_users = users or self.users
        store = profile_store or ProfileStore()
        profiles = {user: store.read(user) for user in target_users}
        for i, u in enumerate(target_users):
            for v in target_users[i + 1 :]:
                prompt = build_prompt(u, v, profiles)
                reply = ai_client.get_response([{"role": "user", "content": prompt}])
                score = _parse_score(reply)
                self.matrix[u][v] = score
                self.matrix[v][u] = score
        self._save()

    def top_matches(self, user: str, top_n: int = 3) -> List[Tuple[str, float]]:
        """Return the top ``top_n`` matches for ``user``."""
        scores = self.matrix.get(user, {})
        return sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_n]
