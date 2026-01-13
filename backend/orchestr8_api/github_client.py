from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional
import os
import requests


@dataclass
class GitHubClient:
    token: str

    def _headers(self) -> dict:
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json",
        }

    def list_issues(self, repo_full_name: str, state: str = "open") -> List[str]:
        url = f"https://api.github.com/repos/{repo_full_name}/issues?state={state}&per_page=100"
        issue_urls: List[str] = []
        while url:
            r = requests.get(url, headers=self._headers(), timeout=30)
            r.raise_for_status()
            for item in r.json():
                if "pull_request" in item:
                    continue
                issue_urls.append(item["html_url"])
            url = self._next_link(r.headers.get("Link"))
        return issue_urls

    def get_issue(self, issue_url: str) -> Tuple[str, str]:
        api_url = issue_url.replace("https://github.com/", "https://api.github.com/repos/")
        if "/issues/" not in api_url:
            raise ValueError("The provided URL does not look like a GitHub issue URL.")
        r = requests.get(api_url, headers=self._headers(), timeout=30)
        r.raise_for_status()
        data = r.json()
        title = data.get("title", "")
        body = data.get("body", "") or ""
        comments_url = data.get("comments_url")
        comments_text = self._fetch_comments(comments_url) if comments_url else ""
        combined = body + ("\n\nComments:\n" + comments_text if comments_text else "")
        return title, combined

    def _fetch_comments(self, comments_url: str) -> str:
        url = comments_url + "?per_page=100"
        parts: List[str] = []
        while url:
            r = requests.get(url, headers=self._headers(), timeout=30)
            r.raise_for_status()
            for c in r.json():
                parts.append(c.get("body") or "")
            url = self._next_link(r.headers.get("Link"))
        return "\n\n---\n\n".join([p for p in parts if p.strip()])

    @staticmethod
    def _next_link(link_header: Optional[str]) -> Optional[str]:
        if not link_header:
            return None
        for chunk in link_header.split(","):
            seg = chunk.strip()
            if 'rel="next"' in seg:
                return seg[seg.find("<")+1:seg.find(">")]
        return None
