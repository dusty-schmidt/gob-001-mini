# Backend Service

The backend is the agent runtime: it provides APIs, orchestrates tools, persists memory, schedules tasks, and emits events for the frontend.

## Features
- Agents & Delegation Engine
- Memory System (user data, fragments, solutions, metadata)
- Task Scheduler (adhoc, planned, cron)
- Behavior Adjustment
- Tools & Helpers Registry (modular Python library)
- Event Bus (WebSocket) + REST API

## Setup

### Requirements
- Python 3.11+
- Redis (events/queues) or compatible broker
- Postgres/SQLite for persistence (configure via ENV)

### Environment
Copy example env and edit values:
```
cp ../ops/env/backend.example.env ../ops/env/backend.env
```
Key variables:
- PORT=8080
- DB_URL=postgresql://... (or sqlite:///local.db for dev)
- REDIS_URL=redis://localhost:6379/0
- ALLOW_ORIGINS=http://localhost:5173
- MODEL_PROVIDER=...

### Install & Run
```
make install
make dev         # starts API and worker; hot reload in dev
# or
python -m src.api
```

## Project Layout
```
src/
  api/                # REST/WS controllers, request/response schemas
  agents/             # agent core, delegation, reasoning, policies
  memory/             # stores, summarizer, retriever, schemas
  scheduler/          # tasks, runners, cron/planner, history
  tools/              # runtime tool interfaces (HTTP, exec, fs, etc.)
  helpers/            # 100+ small python utilities over time
  behavior/           # behavior profiles, merge strategies, validation
  events/             # websocket/event-stream publisher, topics
  knowledge/          # ingestion/indexing interfaces
  logging/            # structured logs, audit trails, redaction hooks
  settings/           # config loader/env management
```

## API Overview
- REST base: `/api/v1`
- WS base: `/ws`

Common endpoints:
- POST `/agents/execute` – run an instruction synchronously
- POST `/tasks` – create task (adhoc/planned/scheduled)
- POST `/behavior/adjust` – merge behavior rules
- POST `/memory/save` – save memory item
- GET  `/memory/query` – query memory by filters
- GET  `/tasks/:id` – task details; GET `/tasks` for list
- WS `/ws/stream` – subscribe to events: `task.update`, `agent.token`, `memory.update`

Schemas live in `docs/api/openapi.yaml`.

## Memory Integration
- Memory writes/reads via `src/memory/`
- Summarizer compresses old context; fragments auto-updated per conversation
- Solutions saved with code artifacts; promotable to tools
- Metadata supports filtering and retention rules

## Scheduler Integration
- JSON task spec accepted by POST `/tasks`
- Types: adhoc, planned (ISO datetimes), scheduled (cron fields)
- Worker executes tasks; status streamed over WS

## Behavior Adjustment
- POST `/behavior/adjust` with rules
- Server validates/merges into active profile; persisted and effective immediately

## Tools & Helpers
- `src/helpers/` contains granular utilities (e.g., `csv_read.py`, `json_merge.py`)
- `src/tools/` wraps helpers into callable tools with uniform interface
- New successful solution → promote to `src/tools/<domain>/` with manifest

## Testing
```
make test
```
- Unit tests for memory, scheduler, tools
- Contract tests for API/WS

## Observability
- Structured logs (JSON)
- Event tracing IDs flow through API → agents → tools → events

[GOB] :: Generalized Operations Bot says: keep your logs clean and your queues greener than envy.
