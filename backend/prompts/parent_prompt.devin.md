# Orchestr8 — Multi‑Agent Orchestration

This text describes how multiple agents were coordinated.

A round‑based routine was used.

- In each round, an agent asked Orchestr8 for the next issue.
- The agent worked the issue using the single‑issue loop.
- The agent reported success or failure to Orchestr8.
- When a failure occurred, a retry plan was appended and the issue was queued again.

Three rounds were typically used so that parallel agents could rotate across issues.
