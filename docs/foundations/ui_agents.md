# UI Agents

Purpose: Make the interface adaptive. Agents decide components, layout, and interaction patterns using backend context and live events.

## Roles (example convention)
- RenderAgent – picks what to render
- LayoutAgent – arranges components
- InteractionAgent – interprets user actions

## Data Contract
```
{
  "component": "ChatTerminal",
  "layout": "fullscreen",
  "theme": "terminal-green",
  "props": {"sessionId": "..."},
  "adaptations": ["mobile-friendly", "kbd-shortcuts"]
}
```

## Integration Points
- Consumes backend REST for control
- Subscribes to WS for streaming output and task updates
- Shares schemas with backend (OpenAPI/JSON Schema)

[GOB] :: Grid Overwatch Bridge: layouts that listen, components that care.
