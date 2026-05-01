---
name: manager-ticket-lifecycle
description: The GitHub issue IS the baton. Manager creates tickets, pre-assigns roles, enforces status transitions through the Agile workflow.
argument-hint: "[action: create|decompose|transition|close] [type: epic|story|task|bug]"
user-invocable: true
disable-model-invocation: false
---

# Ticket-as-Baton Lifecycle

## Core paradigm

The GitHub issue is the **baton**. It carries work through Manager → Collaborator → Admin → Consultant. Each role writes a structured comment on the ticket and transitions the status label — mirroring a Jira card moving across a Scrum board.

## Status workflow (label transitions)

```
backlog → ready → in-progress → review → done
(create)  (scope)  (implement)   (PR/ops)  (close)
```

## Label taxonomy

- **Type**: `type:epic|story|task|bug|doc|research`
- **Status**: `status:backlog|ready|in-progress|review|done`
- **Priority**: `priority:P1|P2|P3`
- **Area**: `area:dashboard|hooks|skills|instructions|agents|scripts|infra`
- **Role** (current holder): `role:manager|collaborator|admin|consultant`

## Manager creates ticket

1. `gh issue create --title "<imperative>" --label "type:..." --label "status:backlog" --label "priority:..." --label "area:..."`
2. Body: description, acceptance criteria, story points, parent epic ref.
3. Add scope comment (see role-manager-execution output contract).
4. Transition: `status:backlog` → `status:ready`, set `role:manager`.
5. Emit `MANAGER_HANDOFF` with `issue: #N`.
6. Swap label: `role:manager` → `role:collaborator`.

## Epic decomposition

For large work, create Epic issue, then sub-issues referencing parent.
Each sub-issue gets its own label set and full lifecycle.

## Parallel dispatch protocol

Manager assigns independent tickets to different collaborators:
- Research → Rex Research (web search, analysis)
- Code impl → Cody Builder (features, fixes)
- UI/CSS → Dash Styles (visual, layout)
- Docs → Petra Prose (technical writing)
All assigned tickets execute concurrently. Each has its own baton.

## Research ticket lifecycle

Research tickets use the full baton but skip branching:
1. No branch created — research produces findings, not code.
2. Collaborator posts research findings as ticket comment.
3. Admin reviews wiki/research/ storage — no merge needed.
4. Consultant validates research quality and wiki placement.

## Role comment protocol

Each role writes **one structured comment** when taking the baton:
- **Manager** 🎯: objective, AC, constraints → "Baton → Collaborator"
- **Collaborator** 🔧: files_changed, validation → "Baton → Admin"
- **Admin** ⚙️: commit, PR, CI, merge → "Baton → Consultant"
- **Consultant** 🔍: confidence, risks, follow-ups → "Baton complete"

## Closing rules

1. Close only after merge + Consultant CLOSEOUT comment.
2. Close comment: version, merge evidence, validation summary.
3. Final label state: `status:done`, all `role:*` labels removed.

## Hard constraints

1. No work without a ticket. 2. Branch: `<type>/<issue#>-<slug>`.
3. Commits reference `#N`. 4. PR body: `Closes #N`.
5. Role comments are permanent audit evidence.

## Definition of Done (per ticket)

- [ ] All acceptance criteria checked
- [ ] Lint + tests pass; docs updated if behavior changed
- [ ] PR merged with `Closes #N`
- [ ] Consultant CLOSEOUT comment posted
- [ ] `status:done` label applied
