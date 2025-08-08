from __future__ import annotations

"""Profile persistence module."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

from ..ai import AIClient
from ..prompts import BUILD_PROFILE_PROMPT
from . import BASE_DIR
from .json_store import JsonStore


@dataclass
class ProfileStore(JsonStore[Dict[str, str]]):
    """Persist conversation summaries per user."""

    base_dir: Path = BASE_DIR / "profiles"
    prompt_template: str = BUILD_PROFILE_PROMPT
    profiles: Dict[str, str] = field(init=False)

    def default_path(self) -> Path:
        return self.base_dir / "profiles.json"

    def default(self) -> Dict[str, str]:
        return {}

    def __post_init__(self) -> None:
        super().__post_init__()
        self.profiles = self.load()

    def update(self, ai_client: AIClient, user: str, text: str) -> None:
        """Send new chat text to the AI and persist the updated profile."""

        existing = self.profiles.get(user, "")
        prompt = self.prompt_template.replace("{info}", existing).replace("{messages}", text)
        response = ai_client.get_response([{"role": "user", "content": prompt}])
        self.profiles[user] = response
        self.save(self.profiles)

    def read(self, user: str) -> str:
        return self.profiles.get(user, "")
