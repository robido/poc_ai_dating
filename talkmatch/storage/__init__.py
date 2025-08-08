from __future__ import annotations

"""Storage package exposing persistence helpers."""

from pathlib import Path

BASE_DIR = Path("data")
BASE_DIR.mkdir(parents=True, exist_ok=True)

from .json_store import JsonStore  # noqa: E402
from .profiles import ProfileStore  # noqa: E402
from .chats import ChatStore  # noqa: E402
from .match_matrix import MatchMatrixStore  # noqa: E402
from .message_counts import MessageCountStore  # noqa: E402

__all__ = [
    "BASE_DIR",
    "JsonStore",
    "ProfileStore",
    "ChatStore",
    "MatchMatrixStore",
    "MessageCountStore",
]
