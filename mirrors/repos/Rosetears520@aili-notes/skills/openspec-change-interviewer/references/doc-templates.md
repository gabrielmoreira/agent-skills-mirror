# OpenSpec Change Interviewer — Document Templates

Use these as *merge-in* templates (do not blindly overwrite). Keep existing author structure when present.

## `tasks.md` (suggested structure)

- A short “Scope + Success” preface (2–6 lines) if missing.
- Checkbox tasks in execution order, each with:
  - `ACCEPT:` (objective pass/fail condition)
  - `TEST:` (runnable command or “Manual: …” steps)

## `proposal.md` (suggested sections)

- `## Why`
- `## Goals`
- `## Non-Goals`
- `## Scope`
- `## Success Metrics`
- `## Impact`
- `## Rollout / Rollback`
- `## Risks`
- `## Open Questions`

## `design.md` (suggested sections)

- `## Summary`
- `## Architecture`
- `## Data Model`
- `## Interfaces`
- `## Key Flows`
- `## Failure Handling`
- `## Security & Privacy`
- `## Observability`
- `## Performance`
- `## Migration / Compatibility`
- `## Alternatives Considered`
- `## Decision Log`
- `## Open Questions`

## `specs/*.md` (delta-friendly pattern)

- `## ADDED|MODIFIED|REMOVED|RENAMED Requirements`
- Each requirement:
  - `### Requirement: <Name>`
  - Narrative requirement text
  - At least one scenario:
    - `#### Scenario: <Name>`
    - `- **GIVEN** ...`
    - `- **WHEN** ...`
    - `- **THEN** ...`

## Traceability (optional but recommended)

Add a short table in the most relevant spec file:

| Ref | Requirement | Design decision | Acceptance / Test |
|-----|-------------|-----------------|-------------------|
| R?  | …           | …               | …                 |

