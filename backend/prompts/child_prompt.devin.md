# Orchestr8 — Issue Execution Loop

This document describes the loop that was used to work a single GitHub issue end‑to‑end.

## Inputs

- The current issue URL was provided by the service endpoint.
- The issue body and comment context were provided alongside the URL.
- A fork URL could be present; when it was absent, work was done on a local clone and a fork was created later.

## Working style

I used a plan‑then‑act approach:

1. I summarized the issue in one paragraph.
2. I produced an execution plan as a numbered list.
3. I applied the smallest set of code changes needed to satisfy the plan.
4. I ran tests or a minimal verification pass.
5. I wrote an outcome summary (what changed, why it worked, and what was still unknown).

## Output format

- The execution plan was written first.
- The outcome summary was written last.
- Patch material was included only when it was requested by the calling workflow.
