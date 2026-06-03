# Initiative Index

This is the triggered T3 compact lookup and durable-history surface for the
initiative. It is not the active plan and must not duplicate sprint closeouts.

## Current Snapshot

- State: `not started`
- Active route: `roadmap.md`
- Retained note: `retained-note.md` after final audit.

## Forecast Snapshot

- Appetite state: `within_appetite`
- Bought or deferred tranche: none.
- Current forecast note: use `roadmap.md` for active Forecast Control.

## Durable Direction

No durable direction has been proved yet.

## Artifact Routes

| ID | Type | Status | Path | Read Trigger |
| --- | --- | --- | --- | --- |
| options | options board | active | `options.md` | initiative-local insertion or closeout check |
| pending | discovery | pending | `discoveries/` | first accepted discovery |
| pending | sprint | pending | `sprints/` | first sprint closeout |

## Trace Routes

| Trace ID | Kind | Status | Tags | Owner | Evidence | Read Trigger |
| --- | --- | --- | --- | --- | --- | --- |
| pending | discovery | pending | n/a | `discoveries/` | n/a | first accepted discovery |

## Update Rules

- Add one compact line for each accepted discovery, completed sprint, evidence
  index, trace route, supersession, and durable decision.
- Promote sequence changes into `roadmap.md`; do not leave them only in a
  discovery or closeout.
- Keep full details in discoveries, sprint decision logs, closeouts, and
  evidence indexes.
