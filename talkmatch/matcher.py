from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

from .ai import AIClient
from .profile import ProfileStore


@dataclass
class Matcher:
    """Compute and store match scores between users."""

    users: List[str]
    path: Path | None = None
    matrix: Dict[str, Dict[str, float]] = field(init=False)

    def __post_init__(self) -> None:
        if self.path and self.path.exists():
            self.matrix = json.loads(self.path.read_text(encoding="utf-8"))
            # ensure all users exist in the matrix
            for u in self.users:
                self.matrix.setdefault(u, {})
                for v in self.users:
                    if u != v:
                        self.matrix[u].setdefault(v, 0.0)
        else:
            self.matrix = {u: {v: 0.0 for v in self.users if v != u} for u in self.users}

    def _save(self) -> None:
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.matrix), encoding="utf-8")

    def clear(self) -> None:
        """Reset all match scores to zero and persist the empty matrix."""
        self.matrix = {u: {v: 0.0 for v in self.users if v != u} for u in self.users}
        self._save()

    def calculate(self, ai_client: AIClient, profile_store: ProfileStore | None = None) -> None:
        """Ask the AI to rate compatibility for each user pair.

        The AI is prompted with the stored profiles of each pair of users and
        expected to return a floating point number between 0 and 1.  The score
        is stored symmetrically in the matrix.  Because our demo only has a
        handful of users we simply perform one request per pair.
        """

        store = profile_store or ProfileStore()
        for i, u in enumerate(self.users):
            profile_u = store.read(u)
            for v in self.users[i + 1:]:
                profile_v = store.read(v)
                prompt = (
                    "Rate the romantic compatibility of the two people on a scale "
                    "from 0 to 1.\n"
                    f"Person A profile:\n{profile_u or 'No information.'}\n"
                    f"Person B profile:\n{profile_v or 'No information.'}\n"
                    "Respond with only the numeric score."
                )
                reply = ai_client.get_response([{"role": "user", "content": prompt}])
                match = re.search(r"0(?:\.\d+)?|1(?:\.0+)?", reply)
                score = float(match.group()) if match else 0.0
                self.matrix[u][v] = score
                self.matrix[v][u] = score
        self._save()

    def top_matches(self, user: str, top_n: int = 3) -> List[Tuple[str, float]]:
        """Return the top ``top_n`` matches for ``user``."""
        scores = self.matrix.get(user, {})
        return sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_n]
