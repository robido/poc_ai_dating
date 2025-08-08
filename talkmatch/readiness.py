from __future__ import annotations

"""Evaluate whether a user's profile satisfies key objectives."""

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .ai import AIClient
from .profile import ProfileStore

BASE_DIR = Path(__file__).resolve().parent


def _load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


READINESS_PROMPT = _load_text(BASE_DIR / "readiness_prompt.txt")


@dataclass
class ReadinessEvaluator:
    """Evaluate profile readiness using an AI model."""

    ai_client: AIClient
    prompt_template: str = READINESS_PROMPT

    def score(self, objectives: Sequence[str], profile: str) -> float:
        prompt = self.prompt_template.replace("{objectives}", "\n".join(objectives)).replace(
            "{profile}", profile
        )
        response = self.ai_client.get_response([
            {"role": "user", "content": prompt}
        ])
        try:
            return float(response.strip())
        except ValueError:
            return 0.0

    def is_ready(self, objectives: Sequence[str], profile: str) -> bool:
        return self.score(objectives, profile) >= 80.0


try:  # Import may be provided by another task.
    from .profile_objectives import PROFILE_OBJECTIVES
except Exception:  # pragma: no cover - optional dependency
    PROFILE_OBJECTIVES: Sequence[str] = []


def is_ready(name: str, profile_store: ProfileStore, ai_client: AIClient) -> bool:
    """Return True if the user's profile covers most objectives."""

    evaluator = ReadinessEvaluator(ai_client)
    profile_text = profile_store.read(name)
    return evaluator.is_ready(PROFILE_OBJECTIVES, profile_text)
