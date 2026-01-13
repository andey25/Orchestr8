from __future__ import annotations

import pathlib

PROMPTS_DIR = pathlib.Path(__file__).resolve().parent.parent / "prompts"


def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    return path.read_text(encoding="utf-8")
