# clawhip × filesystem-offloaded memory

Use this skill when you want a Claw OS-style memory system where `MEMORY.md` stays small and points into a structured `memory/` tree.

## What you get

- a clear role for `MEMORY.md` as pointer/index/current-beliefs layer
- a practical read/write workflow for agents
- guidance for sharding memory by time, channel, project, topic, and handoff
- migration guidance away from monolithic memory files

## Read order

1. Read `MEMORY.md` first.
2. Follow the pointer to the smallest relevant shard.
3. Read subtree indexes only when needed.
4. Avoid loading the whole memory tree by default.

## Write order

1. Write detailed updates to the canonical leaf shard.
2. Update `MEMORY.md` only when the pointer map or current beliefs changed.
3. If a section grows noisy, split it into a dedicated file.
4. Archive cold history to keep the hot path small.

## Default shard map

- `memory/daily/YYYY-MM-DD.md` -> chronological execution log
- `memory/channels/<channel>.md` -> one lane/channel
- `memory/projects/<project>.md` -> project/repo state
- `memory/agents/<agent>.md` -> agent/operator profile
- `memory/topics/rules.md` -> durable operating rules
- `memory/topics/lessons.md` -> reusable lessons
- `memory/handoffs/YYYY-MM-DD-<slug>.md` -> bounded handoffs
- `memory/archive/YYYY-MM/` -> cold history

## Offload triggers

Offload when:

- `MEMORY.md` stops being easy to scan
- one topic dominates the root file
- detail is only relevant to one entity or workflow
- logs or history start crowding out current beliefs

## Start here

- `docs/memory-offload-architecture.md`
- `docs/memory-offload-guide.md`
- `docs/examples/MEMORY.example.md`
- `docs/examples/memory/README.example.md`
