from __future__ import annotations

"""Profile persistence module."""

from dataclasses import dataclass
from pathlib import Path

from ..ai import AIClient
from ..prompts import BUILD_PROFILE_PROMPT
from . import BASE_DIR


@dataclass
class ProfileStore:
    """Persist conversation summaries per user."""

    base_dir: Path = BASE_DIR / "profiles"
    prompt_template: str = BUILD_PROFILE_PROMPT

    def __post_init__(self) -> None:
        self.base_dir.mkdir(exist_ok=True)

    def update(self, ai_client: AIClient, user: str, text: str) -> None:
        """Send new chat text to the AI and persist the updated profile."""

        path = self.base_dir / f"{user}.txt"
        existing = path.read_text(encoding="utf-8").strip() if path.exists() else ""
        prompt = (
            self.prompt_template.replace("{info}", existing).replace("{messages}", text)
        )
        response = ai_client.get_response([{"role": "user", "content": prompt}])
        path.write_text(response + "\n", encoding="utf-8")

    def read(self, user: str) -> str:
        path = self.base_dir / f"{user}.txt"
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")
