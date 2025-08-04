# Memory System

Purpose: Provide hybrid, durable memory for agents to learn and recall across sessions with efficient context usage.

## Structure
- User Data: user-provided facts (names, API keys)
- Fragments: auto-updated conversation nuggets
- Solutions: successful outcomes; code artifacts promotable to tools
- Metadata: ids, timestamps, pii flags, retention policy, tags

## Operations
- save(query): store with metadata
- query(filter): retrieve by tags/time/type
- summarize(conversation): produce structured summaries
- compress(history): multi-level compression preserving originals

## Integration Points
- Backend: `src/memory/` as single interface used by agents/tools
- API: `/memory/save`, `/memory/query`
- Frontend: can display recalled items; user can curate memory entries

## Lifecycles
- Recent → raw
- Aging → summarized
- Old → compressed summary with backlinks to originals

## Privacy & Governance
- PII tagging in metadata
- Redaction hooks in persistence
- Export & purge endpoints

[GOB] :: Guided Optimization Bot whispers: compress the fluff, keep the facts.
