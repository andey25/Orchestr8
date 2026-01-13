from __future__ import annotations

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import RedirectResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated, Optional, List
import os
import datetime

from openai import OpenAI

from .config import get_settings
from .models import IssueSummary, Orchestr8State, IssueState, NextIssueResponse
from .state_store import build_state_store
from .github_client import GitHubClient
from .forking import Forker
from .llm_ranker import IssueRanker
from .prompts import load_prompt


settings = get_settings()
store = build_state_store(settings)

app = FastAPI(title=settings.service_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_allow_origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


FALLBACK_REPO = os.getenv("ORCH_FALLBACK_REPO", "brendanm12345/wordle")


def _now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _github() -> GitHubClient:
    token = os.getenv(settings.github_token_env, "")
    if not token:
        raise HTTPException(status_code=500, detail=f"GitHub token was not found in {settings.github_token_env}.")
    return GitHubClient(token=token)


def _ranker() -> IssueRanker:
    return IssueRanker(settings=settings, client=OpenAI())


@app.get("/", include_in_schema=False)
async def root():
    url = os.getenv("ORCH_PUBLIC_URL", "")
    if url:
        return RedirectResponse(url=url)
    return {"message": "Orchestr8 is online"}


@app.post("/repository/")
async def set_repository_trailing(repository: str = FALLBACK_REPO):
    return await _set_repository(repository)


@app.post("/repository")
async def set_repository(repository: Annotated[str, Body(embed=True)] = FALLBACK_REPO):
    return await _set_repository(repository)


async def _set_repository(repository: str):
    state = store.load()
    state.repository = repository

    issue_urls = _github().list_issues(repository)
    issues = [IssueSummary(title="", body="", url=u) for u in issue_urls]

    enriched: List[IssueSummary] = []
    for issue in issues:
        title, details = _github().get_issue(issue.url)
        enriched.append(IssueSummary(title=title, body=details, url=issue.url))

    ranked_urls: List[str]
    try:
        ranked_urls = _ranker().rank(enriched)
    except Exception:
        ranked_urls = [i.url for i in enriched]

    state.issues = [IssueState(url=u, status="queued", failure_reason="", n_retries=0, updated_at_iso=_now_iso()) for u in ranked_urls]
    store.save(state)
    return ranked_urls


@app.get("/instructions.devin.md", response_class=PlainTextResponse)
async def instructions_child() -> str:
    try:
        return load_prompt("child_prompt.devin.md")
    except Exception:
        raise HTTPException(status_code=404, detail="Instruction file was not available.")


@app.get("/instructions/parent", response_class=PlainTextResponse)
async def instructions_parent() -> str:
    state = store.load()
    if not state.repository:
        return "A repository was not available yet. Polling was expected."
    if not state.issues:
        return "Issues were not available yet. Polling was expected."
    return load_prompt("parent_prompt.devin.md")


@app.post("/reset", response_class=PlainTextResponse)
async def reset_state() -> str:
    state = store.load()
    state.issues = []
    state.repository = ""
    store.save(state)
    return "ok"


@app.get("/rank-issues/pop")
async def pop_next_issue(agent_id: Optional[str] = None) -> NextIssueResponse:
    state = store.load()
    if not state.issues:
        raise HTTPException(status_code=404, detail="No issues were available.")

    # Preference: queued issues with non-empty failure_reason first (manual retry plans get priority)
    def eligible(issue: IssueState) -> bool:
        if issue.status != "queued":
            return False
        if agent_id and issue.processing_by and issue.processing_by != agent_id:
            return False
        return True

    prioritized = [i for i in state.issues if eligible(i) and i.failure_reason.strip()]
    fallback = [i for i in state.issues if eligible(i)]

    current = (prioritized or fallback)
    if not current:
        raise HTTPException(status_code=404, detail="No queued issues were available.")
    issue = current[-1]  # last queued

    issue.status = "processing"
    issue.processing_by = agent_id or issue.processing_by
    issue.updated_at_iso = _now_iso()
    store.save(state)

    title, details = _github().get_issue(issue.url)
    forked_url = ""
    if settings.enable_forking and settings.fork_owner:
        try:
            forked_url = Forker(token=os.getenv(settings.github_token_env, ""), fork_owner=settings.fork_owner).fork_repo(state.repository)
        except Exception:
            forked_url = ""
    return NextIssueResponse(
        current_issue=issue,
        github_data={"issue_title": title, "issue_details": details, "forked_repo": forked_url},
    )


@app.post("/success", response_class=PlainTextResponse)
async def mark_success(issue: Annotated[str, Body()], description: Annotated[str, Body()] = "", pr_link: Annotated[str, Body()] = "") -> str:
    state = store.load()
    for cur in state.issues:
        if cur.url == issue:
            cur.status = "success"
            cur.updated_at_iso = _now_iso()
            break
    store.save(state)
    _notify(f"Success: {issue}", description, pr_link)
    return "ok"


@app.post("/failure", response_class=PlainTextResponse)
async def mark_failure(issue: Annotated[str, Body()], suspected_reason: Annotated[str, Body()] = "") -> str:
    state = store.load()
    for cur in state.issues:
        if cur.url == issue:
            cur.status = "failed"
            cur.failure_reason = (cur.failure_reason or "") + (suspected_reason or "")
            cur.n_retries = int(cur.n_retries or 0) + 1
            cur.updated_at_iso = _now_iso()
            break
    store.save(state)
    _notify(f"Failure: {issue}", suspected_reason, "")
    return "ok"


@app.get("/retry")
async def get_failed_issue() -> dict:
    state = store.load()
    for issue in state.issues:
        if issue.status == "failed":
            return issue.model_dump()
    raise HTTPException(status_code=404, detail="No failed issues were available.")


@app.post("/add_retry", response_class=PlainTextResponse)
async def add_retry(issue: Annotated[str, Body()], new_plan: Annotated[str, Body()] = "") -> str:
    state = store.load()
    for cur in state.issues:
        if cur.url == issue:
            cur.status = "queued"
            cur.failure_reason = (cur.failure_reason or "") + (new_plan or "")
            cur.updated_at_iso = _now_iso()
            break
    store.save(state)
    return "ok"


def _notify(subject: str, description: str, pr_link: str) -> None:
    url = os.getenv("ORCH_NOTIFICATION_WEBHOOK", "")
    if not url:
        return
    try:
        import requests, json
        requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps({
            "subject": subject,
            "body": (description or "") + ("<br/><br/>" + pr_link if pr_link else ""),
            "timeout": 10
        }), timeout=20)
    except Exception:
        return
