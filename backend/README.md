# Orchestr8 Backend

A FastAPI service was used to ingest GitHub issues, rank them, and expose a queue interface for agent consumers. State was persisted via S3 or a local JSON file.

## Structure

- `orchestr8_api/` contained the service modules.
- `prompts/` contained plain‑text prompt files served by the API.
- `main.py` exposed `app` for ASGI servers.

## Environment

- `OPENAI_API_KEY` was expected for LLM ranking.
- `GITHUB_API_KEY` was expected for GitHub API calls.
- `ORCH_USE_S3` selected S3 (`1`) or local storage (`0`).
- `ORCH_S3_BUCKET` and `ORCH_S3_PREFIX` described the S3 destination.
- `ORCH_LOCAL_STATE` and `ORCH_LOCAL_PATCH_DIR` described local persistence paths.
- `ORCH_NOTIFICATION_WEBHOOK` enabled optional notifications.

## Execution

The service was commonly launched via an ASGI server, for example:

`uvicorn main:app --reload`

