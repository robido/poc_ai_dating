from __future__ import annotations

"""Match matrix persistence."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import json

from . import BASE_DIR


@dataclass
class MatchMatrixStore:
    path: Path = BASE_DIR / "match_matrix.json"

    def load(self, users: List[str]) -> Dict[str, Dict[str, float]]:
        if self.path.exists():
            matrix = json.loads(self.path.read_text(encoding="utf-8"))
            for u in users:
                matrix.setdefault(u, {})
                for v in users:
                    if u != v:
                        matrix[u].setdefault(v, 0.0)
            return matrix
        return {u: {v: 0.0 for v in users if v != u} for u in users}

    def save(self, matrix: Dict[str, Dict[str, float]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(matrix), encoding="utf-8")
