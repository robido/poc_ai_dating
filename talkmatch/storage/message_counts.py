from __future__ import annotations

"""Message count persistence."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Tuple
import json

from . import BASE_DIR


@dataclass
class MessageCountStore:
    path: Path = BASE_DIR / "message_counts.json"
    counts: Dict[Tuple[str, str], int] = field(init=False)

    def __post_init__(self) -> None:
        if self.path.exists():
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            self.counts = {tuple(k.split("|")): v for k, v in raw.items()}
        else:
            self.counts = {}

    def increment(self, name1: str, name2: str) -> None:
        pair = tuple(sorted([name1, name2]))
        self.counts[pair] = self.counts.get(pair, 0) + 1
        self.save()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        raw = {"|".join(k): v for k, v in self.counts.items()}
        self.path.write_text(json.dumps(raw), encoding="utf-8")

    def clear(self) -> None:
        self.counts.clear()
        self.save()
