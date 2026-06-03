# Workflow Operation Guide

This guide summarizes the portable `ub-workflow` operating model.

## Model

```text
Product Vision -> Product Options -> Outcome Waves -> Initiatives -> Discoveries -> Sprints
```

## WIP

Default active WIP is one delivery sprint and one discovery per active
initiative. Wave discovery is active only for activation, transition, or
reroute.

## Advancement

1. Refresh status and active pointers.
2. Revalidate stale candidates before delivery.
3. Create or accept discovery when path truth is uncertain.
4. Prepare only the active or next sprint.
5. In reviewed mode, preview first and wait for later approval.
6. When scope pressure appears, present options and tradeoffs before any
   operator decision to cut, defer, reroute, or buy more scope.
7. Close with evidence, outcome and learning review, Forecast Delta,
   mini-retro, and next action.

## Options Boards

Future work may live in root or initiative-local options boards before
commitment. Options are ordered by document order within horizon lanes, but
they are not delivery commitments, status ledgers, or execution queues.

Remove an option after it is promoted, rejected, merged, or completed and the
receiving artifact owns the durable trace. Do not maintain a `Done` lane in
options boards.

Run `scripts/check_workflow_options.py` during wave activation, initiative
closeout, terminal audit, option promotion, and sprint preview from an option.

Structural workflow changes that affect artifact ownership, lifecycle gates,
scaffold output, transition policy, or recovery context need a compact
accepted workflow-improvement decision record.

## Source Routing

Project-root `SOURCE_ATLAS.md` routes source-code work. Bootstrap seeds it once
from visible project roots; later updates happen only when source boundaries or
test topology change.
