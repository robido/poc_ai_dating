from __future__ import annotations

"""Simple user profile storage for TalkMatch."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProfileStore:
    """Persist conversation snippets per user."""

    base_dir: Path = Path("user_profiles")

    def __post_init__(self) -> None:
        self.base_dir.mkdir(exist_ok=True)

    def append(self, user: str, text: str) -> None:
        path = self.base_dir / f"{user}.txt"
        with path.open("a", encoding="utf-8") as f:
            f.write(text + "\n")

    def read(self, user: str) -> str:
        path = self.base_dir / f"{user}.txt"
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")
