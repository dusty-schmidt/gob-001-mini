# Tools & Helpers

Purpose: Provide a large, modular library of Python helpers and formal tools. Keep helpers atomic; promote proven solutions to tools.

## Directory Strategy
- `src/helpers/` – tiny single-purpose modules (e.g., `csv_read.py`, `http_get.py`)
- `src/tools/` – user-callable tools wrapping helpers with validation, timeouts, and logging
- `src/tools/<domain>/` – grouped domain tools (files, web, data, ml, os)

## Tool Manifest
```
{
  "name": "csv_read",
  "version": "1.0.0",
  "inputs": {"path": "string"},
  "outputs": {"rows": "array"},
  "timeout_sec": 10,
  "permissions": ["fs:read"],
  "promoted_from": "solutions/2025-..."
}
```

## Lifecycle
1) Helper created for a need
2) Used in solution; solution validated
3) Promoted to tool with manifest + tests
4) Exposed to agents via registry

## Integration Points
- Backend agent runtime loads tool registry at startup
- Frontend shows tool catalog; can request execution via API

## Testing & Quality
- Unit tests per helper/tool
- Contract tests for tool I/O
- Observability: structured logs + execution IDs

[GOB] :: Generalized Operations Bot: many tiny tools make mighty machines.
