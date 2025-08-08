from __future__ import annotations

"""Chat history persistence."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from . import BASE_DIR
from .json_store import JsonStore


@dataclass
class ChatStore(JsonStore[List[Dict[str, str]]]):
    def default_path(self) -> Path:
        return BASE_DIR / "chats" / "history.json"

    def default(self) -> List[Dict[str, str]]:
        return []
