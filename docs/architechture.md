# Modular AI Agent Framework

A modular, self-improving AI system with a clean separation between Backend (brains, memory, scheduling, tools) and Frontend (adaptive agent-driven UI). Designed for extensibility, observability, and safe iteration by multi-disciplinary teams.

## High-Level Architecture

- Backend (Service/API):
  - Agent runtime, memory system, task scheduler, behavior adjustment, tool/assistant ecosystem, helper library (100+ Python modules over time).
  - Exposes HTTP/WS APIs and an event bus for realtime UI.
- Frontend (SPA/SSR app):
  - UI agents orchestrate components (render/layout/interaction) based on context and backend signals.
  - Consumes backend APIs and subscribes to events for streaming updates.

Data flow:
User → Frontend UI Agents → Backend API → Agents/Tools/Scheduler/Memory → Events/Responses → Frontend UI Agents → UI

## Repository Structure

```
/                      # Root mono-repo
  backend/            # Service: API, agent runtime, memory, scheduler
    src/
    tests/
    README.md
  frontend/           # SPA/SSR app with UI agents
    src/
    tests/
    README.md
  docs/
    architecture/
    foundations/
      memory.md
      scheduler.md
      behavior.md
      tools_and_helpers.md
      ui_agents.md
    api/
      openapi.yaml
    READMEs.md
  ops/
    docker/
    env/
  scripts/
  CONTRIBUTING.md
  LICENSE
```

## Quick Start

1) Backend
- Create env: `cp ops/env/backend.example.env ops/env/backend.env`
- Install deps: `cd backend && make install` (or `pip install -r requirements.txt`)
- Run: `make dev` (starts API + worker)

2) Frontend
- Create env: `cp ops/env/frontend.example.env ops/env/frontend.env`
- Install deps: `cd frontend && npm i`
- Run: `npm run dev`

3) Connect
- Frontend expects `BACKEND_BASE_URL` and `BACKEND_WS_URL` from env.

## Core Concepts

- Agents: Reason, plan, act; can delegate and use tools.
- Memory: Hybrid store (user data, fragments, solutions, metadata) with summarization and retrieval.
- Tools & Helpers: Modular Python library for all background ops; successful code solutions get promoted to reusable tools.
- Scheduler: Ad-hoc, planned, and cron-like scheduled tasks with task definitions serialized as JSON.
- Behavior Adjustment: User instructions mutate active behavior profile safely and persistently.
- UI Agents: Frontend agents pick components, layouts, and patterns based on context and events.

## Integration Contract (Essentials)

- REST for control-plane (create task, adjust behavior, save knowledge)
- WebSocket/EventStream for data-plane (streaming agent outputs, task status)
- Shared JSON schemas in `docs/api/openapi.yaml`

## Security & Privacy
- API keys and secrets in env only.
- Auditable logs, redaction hooks, and PII tagging in memory metadata.

## Contributing
See CONTRIBUTING.md for branch strategy, code style, testing, and release process.

[GOB] :: Generalized Operations Bot approves this plan—backend brains, frontend finesse, one harmonious hive.
