from __future__ import annotations

"""Simple persistence layer for TalkMatch.

This class centralizes all file system interactions so it can later be
replaced by a real database."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple
import json

from .profile import ProfileStore


@dataclass
class Persistent:
    base_dir: Path = Path("data")

    def __post_init__(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)

    # Profile storage -------------------------------------------------
    def profile_store(self) -> ProfileStore:
        return ProfileStore(base_dir=self.base_dir / "profiles")

    # Chat histories --------------------------------------------------
    def chat_history_path(self, name: str) -> Path:
        return self.base_dir / "chats" / f"{name}.json"

    # Match matrix ----------------------------------------------------
    def match_matrix_path(self) -> Path:
        return self.base_dir / "match_matrix.json"

    # Message counts --------------------------------------------------
    def message_counts_path(self) -> Path:
        return self.base_dir / "message_counts.json"

    def load_message_counts(self) -> Dict[Tuple[str, str], int]:
        path = self.message_counts_path()
        if not path.exists():
            return {}
        raw = json.loads(path.read_text(encoding="utf-8"))
        return {tuple(k.split("|")): v for k, v in raw.items()}

    def save_message_counts(self, counts: Dict[Tuple[str, str], int]) -> None:
        path = self.message_counts_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = {"|".join(k): v for k, v in counts.items()}
        path.write_text(json.dumps(raw), encoding="utf-8")
