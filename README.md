# Orchestr8

Orchestr8 is a lightweight orchestration service for turning a repository’s GitHub issues into a queued worklist that can be consumed by one or more agents. A repository was selected, issues were retrieved from GitHub, and a ranked queue was produced. Each issue was then claimed by an agent, processed, and marked as succeeded or failed. When a failure occurred, a retry plan was appended and the issue was re‑queued.

The project was structured as a small FastAPI backend plus a minimal Next.js UI.

## What was included

- A REST API for:
  - repository selection and issue ingestion
  - issue ranking through an LLM (with a safe fallback ordering)
  - queue consumption by multiple agents
  - success / failure reporting and retrying
- A state store that supported S3 or local JSON storage
- Prompt files that were served as plain text for agent tooling
- A small UI that interacted with the API

## Backend

The backend was located in `backend/` and exposed the following endpoints.

- `POST /repository/` and `POST /repository`
  - A repository full name was recorded and issues were fetched and ranked.
- `GET /rank-issues/pop`
  - The next queued issue was returned. An optional `agent_id` query param could be provided and was stored as the current processor.
- `POST /success`
  - The issue status was marked as successful and an optional webhook notification was attempted.
- `POST /failure`
  - The issue status was marked as failed and a retry counter was incremented.
- `GET /retry`
  - The first failed issue was returned.
- `POST /add_retry`
  - A failed issue was returned to the queue and a retry plan string was appended.
- `POST /reset`
  - The stored state was cleared.
- `GET /instructions.devin.md` and `GET /instructions/parent`
  - Prompt text was returned as plain text.

### Backend configuration

Environment variables were used:

- `OPENAI_API_KEY` was used by the ranking model.
- `GITHUB_API_KEY` was used for GitHub API access.
- `ORCH_USE_S3` controlled whether S3 was used (`1`/`0`).
- `ORCH_S3_BUCKET` and `ORCH_S3_PREFIX` controlled S3 location.
- `ORCH_NOTIFICATION_WEBHOOK` optionally enabled status notifications.

The service was typically started with:

`uvicorn main:app --host 0.0.0.0 --port 8080`

## Frontend

A Next.js UI was provided in `frontend/`. It called the backend endpoints and displayed the current queue state.

From `frontend/`:

- `npm install`
- `npm run dev`

The backend base URL was configured in `frontend/src/lib/api.ts`.
