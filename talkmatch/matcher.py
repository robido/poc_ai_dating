from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class Matcher:
    """Compute and store match scores between users."""

    users: List[str]
    matrix: Dict[str, Dict[str, float]] = field(init=False)

    def __post_init__(self) -> None:
        self.matrix = {u: {v: 0.0 for v in self.users if v != u} for u in self.users}

    def calculate(self) -> None:
        """Fill the score matrix with random values."""
        for i, u in enumerate(self.users):
            for v in self.users[i + 1:]:
                score = random.random()
                self.matrix[u][v] = score
                self.matrix[v][u] = score

    def top_matches(self, user: str, top_n: int = 3) -> List[Tuple[str, float]]:
        """Return the top ``top_n`` matches for ``user``."""
        scores = self.matrix.get(user, {})
        return sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_n]
