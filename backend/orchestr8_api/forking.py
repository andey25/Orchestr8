from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import os

from github import Github


@dataclass
class Forker:
    token: str
    fork_owner: str

    def fork_repo(self, repo_full_name: str) -> str:
        g = Github(self.token)
        repo = g.get_repo(repo_full_name)
        forked = repo.create_fork()
        return forked.html_url
