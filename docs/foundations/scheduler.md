# Task Scheduler

Purpose: Run tasks on-demand (adhoc), at fixed times (planned), or on recurring schedules (cron-like).

## Task Spec (JSON)
```
{
  "name": "Weekly report",
  "type": "scheduled",            
  "plan": ["2025-08-10T18:00:00"],
  "schedule": {                     
    "minute": "0",
    "hour": "18",
    "day": "*",
    "month": "*",
    "weekday": "1"
  },
  "system_prompt": "Utility agent ...",
  "prompt": "Generate ...",
  "attachments": [],
  "dedicated_context": true
}
```

## APIs
- POST `/tasks` (create)
- GET `/tasks` (list)
- GET `/tasks/:id` (status & history)
- POST `/tasks/:id/run` (manual run)
- WS `task.update` events for progress

## Integration Points
- Backend workers execute tasks; results stored in memory (solutions)
- Frontend can create tasks via guided forms; subscribes to progress streams

[GOB] :: Generalized Operations Bot: schedule smart, idle less.
