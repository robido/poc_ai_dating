from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Dict, List, Optional, Tuple
import json

from ..persistent import Persistent


@dataclass
class HistoryManager:
    """Handles chat history and message-count persistence."""

    history_path: Optional[Path] = None
    persistent: Optional[Persistent] = None

    message_counts: ClassVar[Dict[Tuple[str, str], int]] = {}

    def __post_init__(self) -> None:
        if self.persistent and not HistoryManager.message_counts:
            HistoryManager.message_counts = self.persistent.load_message_counts()

    # Chat history --------------------------------------------------
    def load_history(self) -> Optional[List[Dict[str, str]]]:
        if self.history_path and self.history_path.exists():
            try:
                return json.loads(self.history_path.read_text(encoding="utf-8"))
            except Exception:
                return None
        return None

    def save_history(self, messages: List[Dict[str, str]]) -> None:
        if not self.history_path:
            return
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self.history_path.write_text(json.dumps(messages), encoding="utf-8")

    # Message counts ------------------------------------------------
    def increment_message_count(self, name1: str, name2: str) -> None:
        pair = tuple(sorted([name1, name2]))
        HistoryManager.message_counts[pair] = HistoryManager.message_counts.get(pair, 0) + 1
        if self.persistent:
            self.persistent.save_message_counts(HistoryManager.message_counts)

    @classmethod
    def clear_message_counts(cls, persistent: Optional[Persistent] = None) -> None:
        cls.message_counts.clear()
        if persistent:
            persistent.save_message_counts({})
