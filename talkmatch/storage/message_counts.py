from __future__ import annotations

"""Message count persistence."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Tuple

from . import BASE_DIR
from .json_store import JsonStore


@dataclass
class MessageCountStore(JsonStore[Dict[Tuple[str, str], int]]):
    counts: Dict[Tuple[str, str], int] = field(init=False)

    def default_path(self) -> Path:
        return BASE_DIR / "message_counts.json"

    def default(self) -> Dict[Tuple[str, str], int]:
        return {}

    def serialize(self, data: Dict[Tuple[str, str], int]) -> Dict[str, int]:
        return {"|".join(k): v for k, v in data.items()}

    def deserialize(self, raw: Dict[str, int]) -> Dict[Tuple[str, str], int]:
        return {tuple(k.split("|")): v for k, v in raw.items()}

    def __post_init__(self) -> None:
        super().__post_init__()
        self.counts = self.load()

    def increment(self, name1: str, name2: str) -> None:
        pair = tuple(sorted([name1, name2]))
        self.counts[pair] = self.counts.get(pair, 0) + 1
        self.save(self.counts)

    def clear(self) -> None:
        self.counts.clear()
        self.save(self.counts)
