---
name: global-task-router
description: Classify tasks into free, fleet, or premium lanes and persist an escalation rationale for the active session.
argument-hint: "[mode: classify|route|audit] [task-summary]"
user-invocable: true
disable-model-invocation: false
---

# Global Task Router

## Purpose

Route each substantive task through the lowest adequate lane:
**Free -> Fleet -> Premium**.

## Scope boundary

Owns task-lane selection and escalation evidence.
Does not own repository standards, release flow, or deployment.

## Hard constraints

1. Default to the lowest adequate lane.
2. Premium requires explicit justification.
3. Persist lane evidence when hooks are available.
4. Prefer existing tool calls over extra user prompts.
5. Recommend manual picker changes only when no API exists.

## Decision flow

1. Read task intent and repo context.
2. Score for `free`, `fleet`, and `premium` triggers.
3. Select the highest required lane.
4. Emit backend/model recommendation.
5. Record rationale and escalation trigger.

## Lane guidance

- **Free**: search, explain, docs, boilerplate, small edits, simple bugfixes.
- **Fleet**: medium multi-file implementation, test writing, migrations, patterned refactors.
- **Premium**: architecture, ambiguous debugging, risky changes, security, performance, concurrency.

## Escalation triggers

Move upward when any of these are true:
- lower lane already failed
- ambiguity is high
- task spans many files/systems
- reasoning quality changes likely avoid retries
- speed-to-correctness matters more than raw request cost

## Output format

```text
TASK_ROUTER_REPORT
lane: <free|fleet|premium>
backend: <auto|openclaw|sonnet>
recommended_model: <model-or-picker>
confidence: <high|medium|low>
rationale:
triggers:
```

## Verification

- Hook state contains routing metadata.
- Prompt hook injects lane context on substantive prompts.
- Router CLI returns JSON for sample prompts.
- Repository lint still passes.
- **Fleet dispatch is operational**: `node scripts/global/task-router-dispatch.js --prompt "implement multi-file refactor" --execute` routes to the fleet inference endpoint (resolved via `fleet-config.js`) and returns a model response.
- Successful fleet dispatches are logged to `~/.copilot/openclaw-usage.log` via `openclaw-lane-log.js`.
- `openclaw-chat.js --health` confirms gateway reachability before dispatch.
