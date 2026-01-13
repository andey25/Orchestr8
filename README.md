# Orchestr8

Orchestr8 is a system that coordinates multiple AI agents to analyze software repositories, generate task plans, execute actions, and track outcomes through a central API.

The platform exposes a backend service and a browser-based frontend. The backend manages issues, agents, execution state, and evaluation metrics. The frontend presents a live interface for viewing queues, agent activity, and result summaries.

## System overview

Orchestr8 operates around a queue of issues. Each issue represents a unit of work such as code review, test generation, or refactoring. Agents request work from the queue, receive an execution plan, and submit results back to the system.

The backend stores all state in a persistent database and exposes a REST API. Agents and the frontend communicate exclusively through this API.

## Backend

The backend runs as a Python web service. It provides endpoints for:

- registering and managing issues  
- assigning issues to agents  
- tracking execution status  
- collecting outputs and metrics  
- exposing system state to the frontend  

The service starts from `main.py` and loads configuration from environment variables. Database models, routing, and agent coordination live under the backend package.

## Agents

Agents are logical workers that pull tasks from the queue. Each agent has an identifier and maintains its own execution history. The system supports multiple concurrent agents operating on the same issue pool.

An agent requests work, receives a plan, performs the required actions, and submits a structured result. The backend records these results and updates the issue state.

## Frontend

The frontend is a web application that connects to the backend API. It displays:

- active issues  
- agent assignments  
- execution status  
- result summaries  

The UI polls the API and renders the current system state in real time.

## Running the system

The backend runs by installing the Python dependencies and starting the service entry point. The frontend runs as a standard web application that connects to the backend URL.

Configuration such as database location, API port, and model settings is provided through environment variables.

## Data flow

1. Issues are created and stored in the backend.  
2. Agents request the next available issue.  
3. The backend returns an execution plan.  
4. The agent performs the work and submits results.  
5. The backend records outputs and updates system state.  
6. The frontend displays the updated information.

## Evaluation

Orchestr8 tracks outcomes for each issue, including completion status, execution time, and agent outputs. These records support comparison across agents and runs.

## Structure

The repository contains a backend directory for the API service and a frontend directory for the web interface. Supporting modules define models, routing, and agent coordination logic.
