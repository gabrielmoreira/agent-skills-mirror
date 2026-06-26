---
name: controlflow-orchestration
description: "Use when executing an approved multi-phase plan in Cursor, with gates, approvals, retries, and Task delegation to controlflow subagents."
---

# ControlFlow Orchestration (Cursor)

## Overview

Execute an approved plan with explicit state, disciplined gates, bounded retries, and local evidence. Does not use VS Code `agent/runSubagent`.

## Local Contract

- Start from `plans/<task-slug>-plan.md`; use `controlflow-planning` if missing.
- Confirm strict plan review before non-trivial execution.
- Track current phase, last verification, blocker, and next action.

## Workflow

1. Confirm plan path, phase, target files, validation command, approval needs.
2. Verify review routing: `SMALL` → plan audit; `MEDIUM`/`LARGE` → assumption verifier; `LARGE` → executability verifier; `HIGH` risk → assumption verifier.
3. If review blocks, revise plan before implementation.
4. Serialize phases unless write ownership is clearly disjoint.
5. **Delegation:** For each phase `executor_agent`, prefer Task to the matching `.cursor/agents/controlflow-*.md` subagent. Parent must not implement when an implementer subagent is assigned.
6. Use `references/failure-taxonomy.md` and `references/runtime-policy.json` for retry/replan.
7. Gate destructive actions behind explicit user approval (Cursor AskQuestion when appropriate).
8. After each phase, run phase checklist; update plan lifecycle sections.
9. Save artifacts under `plans/artifacts/<task-slug>/`.

## Task Delegation Examples

| Phase role | subagent_type |
| ---------- | ------------- |
| CodeMapper | `controlflow-code-mapper` |
| Researcher | `controlflow-researcher` |
| Core implementer | `controlflow-core-implementer` |
| UI implementer | `controlflow-ui-implementer` |
| Platform | `controlflow-platform-engineer` |
| Docs | `controlflow-technical-writer` |
| Browser test | `controlflow-browser-tester` |
| Code review gate | `controlflow-code-reviewer` |

**Fallback:** Execute the role instructions in the parent session using the matching skill; record that fallback in the plan `## Decision Log`.

## Stop-the-Line

Stop when verification fails, assumptions break, security risk appears, or approval is missing. Classify failures per failure taxonomy before retry.

## References

- `references/runtime-policy.json`
- `references/failure-taxonomy.md`
- `references/phase-checklist.md`
- `docs/agent-engineering/CURSOR-SUPPORT.md`
