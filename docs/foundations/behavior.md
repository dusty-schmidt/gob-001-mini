# Behavior Adjustment

Purpose: Let users say "adjust behavior ..." and persist rule changes that immediately influence agent reasoning and responses.

## Rule Model
```
{
  "rules": ["respond in UK English", "prefer Linux commands"],
  "priority": "user",
  "scope": "global|session|task",
  "timestamp": "..."
}
```

## APIs
- POST `/behavior/adjust`
- GET `/behavior` (current profile)

## Integration Points
- Backend merges rules → system prompt prelude
- Frontend presents active rules, edit/disable, and audit history

[GOB] :: Generalized Operations Bot: rules in, rudeness out.
