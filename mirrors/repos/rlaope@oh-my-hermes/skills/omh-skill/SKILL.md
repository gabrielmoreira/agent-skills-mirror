---
name: omh-skill
description: [omh] Hermes adaptation for managing local skills. Use when the user says: skill, skills, manage skills.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, operator]
    category: operator
    phase: skill-management
    role: tracker
    quality_tier: evidence-gated
---

# Skill

This is a Hermes-native `skill` workflow skill.

## Why This Exists

`skill` exists to keep `operator` work explicit, evidence-backed, and inside the Hermes/executor boundary instead of relying on ad hoc chat narration.

## Do Not Use When

- The request is casual chat, a status-only acknowledgement, or another workflow has stronger routing evidence.
- The user needs implementation, review, CI, merge, or external publishing evidence that has not been delegated or observed.

## Examples

Good example:

- Prompt: $skill list installed OMH skills and show the catalog metadata for each workflow.
- Expected behavior: Manage or inspect the skill catalog without claiming runtime execution or external evidence.
- Why: The request is operator skill management, not a user workflow run.

Bad example:

- Prompt: skill: treat casual chat or unaccepted work as if this workflow already produced verified results.
- Expected behavior: Ask a clarification question or route to a narrower workflow instead of forcing `skill`.
- Why: The request lacks the required inputs or would overclaim work that Hermes did not observe.

## Completion Checklist

- The local command, managed path, config surface, and state artifact inspected are named.
- Blocking issues, warnings, and optional surfaces are separated.
- The next repair action is explicit and does not claim a reload or runtime observation.

## Recovery Notes

- If a managed path or config key is missing, route to setup/update repair instead of editing hidden state.
- If a reload or plugin load was not observed, keep the diagnostic result as local health evidence only.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `buzz`, `agent-board`, `gateway-intent-card`, `+34 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use for local skill listing, search, add, remove, or edit tasks.

    Strong routing signals: `skill`, `$skill`, `skills`, `manage skills`

## Catalog Metadata

Category: `operator`
Phase: `skill-management`
Hermes role: `tracker`
Quality tier: `evidence-gated`
Reasoning demand: `light`

Quality bar:

- Name the workflow target, constraints, validation evidence, and stop condition.
- Separate Hermes guidance from executor or wrapper behavior unless evidence proves the step happened.

Handoff policy:

Use Hermes for inventory and guidance; delegate only repository code changes to the selected coding executor.

Required inputs:

- skill action
- target skill name or directory

Expected outputs:

- skill inventory or mutation result
- verification note

Artifact expectations:

- manifest update when managed skills change

Safety rules:

- Do not imply hidden Hermes runtime behavior.
- Use the smallest verification that can prove the claim.

## Runtime Evidence

Preferred harness for this skill: `docs-specialist`.

```sh
omh runtime record --skill skill --harness docs-specialist --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
