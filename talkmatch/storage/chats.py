from __future__ import annotations

"""Chat history persistence."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import json

from . import BASE_DIR


@dataclass
class ChatStore:
    path: Path | None = None

    def __post_init__(self) -> None:
        if self.path is None:
            self.path = BASE_DIR / "chats" / "history.json"

    def load(self) -> Optional[List[Dict[str, str]]]:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                return None
        return None

    def save(self, messages: List[Dict[str, str]]) -> None:
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(messages), encoding="utf-8")
