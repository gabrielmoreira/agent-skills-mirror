---
name: role-collaborator-execution
description: Implement scoped changes and produce validation evidence matching manager-defined gates.
argument-hint: [change-scope: small|medium|large]
user-invocable: true
disable-model-invocation: false
---

# Role: Collaborator Execution

## Responsibilities

- Implement only manager-scoped changes.
- Keep edits minimal and localized.
- Run required validation gates and capture outcomes.
- Update docs/changelog when behavior changes.

## Upstream verification (from Manager)

Before implementing, verify Manager's scope:
- Are acceptance criteria testable and complete (binary pass/fail)?
- Are constraints realistic given available resources?
- Are verification gates achievable? If not, push back early.
- If scope is vague, request `MANAGER_HANDOFF` revision.

## Entry criteria

- Valid `MANAGER_HANDOFF` exists.
- Required gates are defined.
- Active GitHub issue linked to work.

## Branch and commit rules

- Create branch: `<type>/<issue#>-<slug>` (e.g., `feat/62-baton-redesign`).
- Every commit references `#N` in message.
- Pull latest `main` into branch before PR: `git pull origin main`.
- Research tickets: no branch — post findings as ticket comment.

## Exit criteria

- `COLLABORATOR_HANDOFF` includes concrete validation evidence.
- `COLLABORATOR_HANDOFF` explicitly enumerates `admin_required_ops`.
- Do not declare complete at exit; "all gates pass" = validated, not released.
- Any scope drift is explicitly flagged for manager re-handoff.

## Rich comment template

`COLLABORATOR_HANDOFF` comment must include:
- **Changes**: per-file summary of what changed and why
- **Behavior delta**: before/after description of observable behavior
- **AC evidence**: each AC checkbox ✅ with the test command or output proving it
- **Risks for Admin**: potential CI flags, merge conflict risk, env dependencies
- **Visualization** (optional): Mermaid diagram or ASCII flow for complex changes

Add 🔧 reaction: `gh api repos/{owner}/{repo}/issues/{N}/reactions -f content=wrench`

## Multi-ticket TODO model

When multiple tickets are in `status:todo`, the Collaborator:
- Holds ALL of them in TODO simultaneously (visible in baton map).
- Keeps **exactly one** in `status:in-progress` at a time.
- Completes and emits `COLLABORATOR_HANDOFF` before pulling the next ticket to `in-progress`.

This prevents context bleed and ensures clean per-ticket evidence trails.

## Ticket baton protocol

1. Write comment — **first line**: `**🔧 Collaborator [role-collaborator-execution] — <persona>**`
   then: `## Validation Evidence (#N)`.
2. Transition labels: `status:todo` → `status:in-progress`, confirm `role:collaborator`.
3. **AC confirmation gate**: Before COLLABORATOR_HANDOFF, mark each AC checkbox ✅ or ❌ with evidence. All must be ✅ to proceed.
4. On COLLABORATOR_HANDOFF: swap `role:collaborator` → `role:admin`.
5. **Emit event**: `emit-event.js --type baton:collaborator --issue N --role collaborator --agent "<persona>"`.

**Persona roster**: see `agents/roster.json`. Select persona matching task specialty.

## Must not do

- Do not alter scope without manager handoff update.
- Do not perform final release/merge/admin governance decisions.

## Escalation triggers

- Missing gate evidence.
- Ambiguous acceptance criteria.

## Output contract

```text
COLLABORATOR_HANDOFF
files_changed:
behavior_changes:
validation_results:
docs_updates:
admin_required_ops:
open_risks:
```
