# Workflow Agent Orientation

Use the portable `ub-workflow` skill as the workflow contract. This file is a
thin operations-root reminder, not a duplicate rulebook.

## Resume Order

1. `status.md`
2. `vision.md` only when product direction matters
3. root `options.md` for transition, future-work lookup, or option promotion
4. active `waves/wNN-*/wave.md`
5. active initiative or discovery named by status
6. initiative-local `options.md` for insertion, closeout, or transition checks

## Local Rules

- Keep status compact and current.
- Update status by replacing current facts, not by appending chronology.
- Use root `options.md` for curated product-level, future-wave, and
  unknown-owner options. It is pre-commitment memory, not a backlog ledger or
  execution queue.
- Use initiative-local `options.md` only for possible insertions before that
  initiative closes.
- Remove options after promotion, rejection, merge, or completion once the
  receiving artifact owns the durable trace. Do not maintain a `Done` lane.
- Run `scripts/check_workflow_options.py` from the shared `ub-workflow` skill
  during wave activation, initiative closeout, terminal audit, option
  promotion, and sprint preview from an option.
- Store detail in the owner artifact.
- Do not execute a sprint without accepted discovery or reviewed preview.
- When forecast pressure appears, present options and tradeoffs, then wait for
  explicit operator decision before cutting, deferring, rerouting, or buying
  more scope.
- Keep one active sprint and one active discovery per active initiative unless
  status records an explicit exception.
- Before activating a new wave or initiative, review root options and
  unresolved local options from the closing initiative.
- Structural workflow changes that affect artifact ownership, lifecycle gates,
  scaffolding, transition policy, or recovery context need a compact accepted
  workflow-improvement decision record.
