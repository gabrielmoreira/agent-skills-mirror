---
name: topology-mutation-and-seat-management
description: Use when changing a rig while it is alive — `rig expand` / `rig shrink` / `rig launch` / `rig remove` / `rig discover` / `rig bind` / `rig adopt` / `rig attach`. Covers the 4 failure modes (newly created seat lacks queue/startup/role; edges and permissions not updated; adopt/bind succeeds at tmux but not OpenRig identity; shrink/remove leaves stale topology references) and the rule that mutation must work while the rig is active, not just in clean fixtures.
metadata:
  cli_surfaces_referenced:
    - adopt
    - attach
    - bind
    - discover
    - expand
    - launch
    - ps
    - release
    - remove
    - shrink
    - unclaim
    - up
    - whoami
  openrig:
    stage: factory-approved
    sibling_skills:
      - rig-lifecycle
      - seat-scaling-and-specialization
      - cross-host-rig-commands
      - sidecar-operator
      - rig-bundles-and-shareable-artifacts
      - specification-system
      - extension-and-user-workspace
---

# Topology Mutation and Seat Management

The ability to change a rig **while it is alive**: expand, shrink,
launch, remove, discover, bind, adopt, and attach seats or sessions.
Seat management includes the **stable identifiers, edges, roles, and
startup context** that make those mutations coherent.

**OpenRig should be easy to reach for.** A user should be able to add
capacity, retire capacity, adopt an existing session, or attach a
terminal **without rebuilding the whole topology.** If mutation is
rarely tested, users avoid it and the product collapses back into
static launch scripts.

## Use this when

- Adding capacity to a running rig (`rig expand <rig> <pod-fragment-path>`)
- Removing capacity (`rig shrink` / `rig remove`)
- Launching/relaunching a node in a running rig (`rig launch`)
- Binding a discovered session into an existing logical node (`rig bind`)
- Adopting a topology + binding live sessions (`rig adopt`)
- Attaching a shell or agent into a rig node (`rig attach --self`)

## Don't use this when

- The rig is being created fresh from scratch — use `rig up` (lifecycle, not mutation)
- The intent is to scale specifically (add specialized capacity) — use `seat-scaling-and-specialization` skill
- The intent is occupant replacement on a stable seat — use `seat-continuity-and-handover` skill

## Failure modes (4)

1. **A newly created seat lacks the queue, startup context, or role files it needs to operate.** Topology mutation creates the seat, but the seat needs more than a tmux session to be useful.
2. **Edges and permissions are not updated when a seat is added or removed.** Topology references go stale; later workflows route to nonexistent seats.
3. **Adopt/bind succeeds at the tmux/session layer but not at the OpenRig identity layer.** The session is attached but `rig whoami` doesn't know about it; downstream consumers see partial state.
4. **Shrink/remove leaves stale topology references that later workflows route into.** Cleanup is part of the operation, not an afterthought.

## Proof standard

Proof must cover **mutation while a rig is active**, not just in a
clean test fixture. The useful matrix:

| Operation | What to verify |
|---|---|
| Add seat | New seat has queue, startup context, role; `rig whoami` resolves it |
| Remove seat | Stale references cleaned; edges/permissions updated |
| Adopt existing session | tmux session bound at OpenRig identity layer; `rig whoami` reports correctly |
| Attach observer terminal | External CLI attachment recorded |
| Verify topology projections after each move | `rig ps --nodes` reflects current truth, not pre-mutation cache |

A clean-fixture proof is necessary but not sufficient. Live-rig proof
catches the failure modes that fixture-mode misses.

## Stable roles during topology changes

Capacity changes must preserve useful roles, routing and durable work. Distinguish
adding or removing a seat from replacing its occupant; use
`seat-continuity-and-handover` for the latter.

## Currently shipped surfaces

Per `cli-reference.md` v0.2.0:

- `rig expand <rig-id> <pod-fragment-path>` (with optional `session_source`)
- `rig shrink <rigId> <podRef>`
- `rig launch <rigId> <nodeRef>`
- `rig remove <rigId> <nodeRef>`
- `rig discover [--draft]`
- `rig bind <discoveredId> --rig <rigId> (--node <id> | --pod <ns> --member <name>)`
- `rig adopt <path> --bind <logicalId=tmuxSessionOrDiscoveryId>`
- `rig attach --self --rig <rigId> --node <logicalId>`
- `rig unclaim <sessionRef>` / `rig release <rigId>`

## Choose the proving environment and authority

Select an isolated active rig or an explicitly authorized live target for the
relevant operation. Record its running build, before/after topology, continuity
and outstanding work. A passing schema check or isolated fixture does not prove
an existing live rig was changed correctly. A runtime timeout is indeterminate
until its durable and process effects are reconciled; do not retry blindly.

The matrix above is verification guidance, not permission to modify another
rig. Name the operation's owner and scope, preserve the state needed for recovery,
and retain missing or failed checks in the result. No local experiment or
unfinished proof obligation is implied by loading this skill.

## See also

- `openrig-user` skill — CLI surface for `rig expand / shrink / launch / remove / bind / adopt / attach`
- `seat-scaling-and-specialization` skill — when to add specialized capacity vs generic
- `seat-continuity-and-handover` skill — replacing an occupant on a stable seat (different shape than topology mutation)
- `cross-host-rig-commands` skill — cross-host topology mutation (deferred)
