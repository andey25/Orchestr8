from __future__ import annotations

from dataclasses import dataclass
from typing import List
import json

from openai import OpenAI

from .models import IssueSummary
from .config import Settings


@dataclass
class IssueRanker:
    settings: Settings
    client: OpenAI

    def rank(self, issues: List[IssueSummary]) -> List[str]:
        if not issues:
            return []
        prompt_lines = []
        for i, issue in enumerate(issues, start=1):
            prompt_lines.append(
                f"{i}: Title: {issue.title}\nBody: {issue.body}\nURL: {issue.url}"
            )
        user_prompt = "\n\n".join(prompt_lines)

        system = (
            "A list of GitHub issues will be provided. "
            "A JSON array of the issue URLs will be returned, ordered from highest priority to lowest. "
            "Only valid JSON will be returned."
        )

        resp = self.client.chat.completions.create(
            model=self.settings.openai_model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user_prompt}],
            temperature=self.settings.openai_temperature,
        )
        raw = (resp.choices[0].message.content or "").strip()
        ranked = json.loads(raw)
        if not isinstance(ranked, list) or not all(isinstance(x, str) for x in ranked):
            raise ValueError("The model output did not contain a JSON list of URLs.")
        return ranked
