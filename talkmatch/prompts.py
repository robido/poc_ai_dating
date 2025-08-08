from __future__ import annotations

"""Load static text prompts for the TalkMatch project."""

from pathlib import Path
from typing import Dict

BASE_DIR = Path(__file__).resolve().parent


def _load_text(path: Path) -> str:
    """Return the file contents or an empty string if missing."""
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


AMBASSADOR_ROLE: str = _load_text(BASE_DIR / "ambassador_role.txt")
GREETING_TEMPLATE: str = _load_text(BASE_DIR / "greeting_template.txt")
BUILD_PROFILE_PROMPT: str = _load_text(BASE_DIR / "build_profile.txt")
COLLECT_INFO_PROMPT: str = _load_text(BASE_DIR / "collect_info_prompt.txt")

PERSONA_DESCRIPTIONS: Dict[str, str] = {}
_persona_dir = BASE_DIR / "persona_descriptions"
if _persona_dir.exists():
    for path in sorted(_persona_dir.glob("*.txt")):
        try:
            PERSONA_DESCRIPTIONS[path.stem] = path.read_text(encoding="utf-8").strip()
        except OSError:
            continue
