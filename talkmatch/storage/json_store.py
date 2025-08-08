from __future__ import annotations

"""Base class for JSON-backed storage helpers."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generic, TypeVar
import json

T = TypeVar("T")


@dataclass
class JsonStore(Generic[T]):
    """Provide common path setup and JSON load/save helpers."""

    path: Path | None = None

    def __post_init__(self) -> None:
        if self.path is None:
            self.path = self.default_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    # Methods for subclasses to customize ---------------------------------
    def default_path(self) -> Path:  # pragma: no cover - abstract
        raise NotImplementedError

    def default(self) -> T:  # pragma: no cover - abstract
        raise NotImplementedError

    def serialize(self, data: T) -> Any:
        return data

    def deserialize(self, raw: Any) -> T:
        return raw  # type: ignore[return-value]

    # Public API -----------------------------------------------------------
    def load(self) -> T:
        if self.path.exists():
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                return self.deserialize(raw)
            except Exception:
                pass
        return self.default()

    def save(self, data: T) -> None:
        self.path.write_text(json.dumps(self.serialize(data)), encoding="utf-8")
