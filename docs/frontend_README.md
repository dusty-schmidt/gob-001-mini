# Frontend App (UI Agents)

An adaptive UI driven by frontend agents that select components, layouts, and patterns based on user context and backend events.

## Features
- UI Agent layer (render, layout, interaction roles by convention)
- Component registry + plugin adapters
- Realtime streams from backend (WS) for progressive rendering
- Accessible, responsive, themeable UI

## Setup

### Requirements
- Node 18+

### Environment
```
cp ../ops/env/frontend.example.env ../ops/env/frontend.env
```
Key variables:
- VITE_BACKEND_BASE_URL=http://localhost:8080/api/v1
- VITE_BACKEND_WS_URL=ws://localhost:8080/ws/stream

### Install & Run
```
npm i
npm run dev
```

## Project Layout
```
src/
  agents/
    RenderAgent.ts
    LayoutAgent.ts
    InteractionAgent.ts
  components/
    registry.ts        # maps logical component names → React components
    ChatTerminal.tsx
    Dashboard.tsx
  services/
    api.ts             # REST client
    ws.ts              # WebSocket client
    context.ts         # app-wide context (user prefs, task state)
  state/
    stores.ts          # lightweight state
  utils/
    schema.ts          # shared schemas for messages/events
```

## UI Agent Loop
1) User action dispatched → InteractionAgent interprets intent
2) RenderAgent selects component and props based on context and backend state
3) LayoutAgent places components and manages responsive layout
4) Subscribes to `/ws/stream` topics for live updates

## Integration with Backend
- REST for initiating tasks, behavior changes, memory ops
- WS for streaming agent output and task status
- Shared JSON schemas in `docs/api/openapi.yaml`

## Testing
- Component tests (React Testing Library)
- Contract tests using mocked OpenAPI schemas

[GOB] :: Grid Overwatch Bridge confirms: your WS streams shall flow like molten UI.
