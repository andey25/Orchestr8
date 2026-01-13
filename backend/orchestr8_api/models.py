from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict


class IssueSummary(BaseModel):
    title: str
    body: str
    url: str


IssueStatus = Literal["queued", "processing", "success", "failed"]


class IssueState(BaseModel):
    url: str
    status: IssueStatus = "queued"
    failure_reason: str = ""
    n_retries: int = 0
    processing_by: Optional[str] = None
    updated_at_iso: Optional[str] = None


class Orchestr8State(BaseModel):
    repository: str = ""
    issues: List[IssueState] = Field(default_factory=list)


class NextIssueResponse(BaseModel):
    current_issue: IssueState
    github_data: Dict[str, str]
