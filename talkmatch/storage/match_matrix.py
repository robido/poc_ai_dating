from __future__ import annotations

"""Match matrix persistence."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from . import BASE_DIR
from .json_store import JsonStore


@dataclass
class MatchMatrixStore(JsonStore[Dict[str, Dict[str, float]]]):
    def default_path(self) -> Path:
        return BASE_DIR / "match_matrix.json"

    def default(self) -> Dict[str, Dict[str, float]]:
        return {}

    def load(self, users: List[str]) -> Dict[str, Dict[str, float]]:  # type: ignore[override]
        matrix = super().load()
        for u in users:
            matrix.setdefault(u, {})
            for v in users:
                if u != v:
                    matrix[u].setdefault(v, 0.0)
        return matrix
