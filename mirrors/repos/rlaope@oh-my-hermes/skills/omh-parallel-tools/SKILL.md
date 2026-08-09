---
name: omh-parallel-tools
description: [omh] Hermes Parallel Tools workflow: check version currency and parallel-tool capability status, then apply an update only after diff approval. Use when the user says: parallel-tools, parallel tools, hermes parallel tools setup, update hermes for parallel tools, check parallel tool support, enable parallel tool calls, verify parallel tools capability, check hermes version for parallel tools.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, hermes-setup]
    category: hermes-setup
    phase: setup
    role: guide
    quality_tier: hermes-setup-gated
---

# Parallel Tools

This is a Hermes-native `parallel-tools` workflow skill.

## Why This Exists

`parallel-tools` exists to give a quick, read-first answer to whether parallel tool calls are current and enabled, with an update path only when currency is actually missing.

## Do Not Use When

- The user wants a general Hermes update unrelated to parallel-tool capability.
- No version or capability question has been asked yet.
- The request needs a repository code change rather than a local version check.

## Examples

Good example:

- Prompt: update hermes for parallel tools — can you check if I'm on a current enough version?
- Expected behavior: Read the installed version and capability status, report whether parallel tools are current, and hand back a user-runnable update command if not.
- Why: The request is a version-currency and capability check, the core of this skill.

Bad example:

- Prompt: parallel-tools: update your memory with what we discussed.
- Expected behavior: Route to a memory workflow instead of a version-currency check.
- Why: Memory update is unrelated to parallel-tool capability or Hermes version.

## Completion Checklist

- If a prerequisite is unmet, mark that item "not applicable" and continue with the rest of the guide instead of blocking or guessing.
- Success is applicable-only: verification passes when every applicable item is confirmed complete, not when every possible item exists.
- The reported capability status matches an observed read, not an assumed default.

## Recovery Notes

- If the installed version cannot be read, report the read failure and stop before recommending an update.
- If the update command is unavailable for the user's install path, name the blocker instead of guessing a fix.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `agent-board`, `gateway-intent-card`, `voice-operator`, `+33 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when the user wants Hermes to check whether parallel tool calls are current and enabled, run a version-currency check, or report capability status, following the shared prerequisite-check, diagnose, guide, diff-approved apply, and verify contract.

    Strong routing signals: `parallel-tools`, `parallel tools`, `hermes parallel tools setup`, `update hermes for parallel tools`, `check parallel tool support`, `enable parallel tool calls`, `verify parallel tools capability`, `check hermes version for parallel tools`, `헤르메스 업데이트 확인해줘`, `병렬 도구 설정`, `병렬 툴 확인`, `헤르메스 병렬 도구`

## Catalog Metadata

Category: `hermes-setup`
Phase: `setup`
Hermes role: `guide`
Quality tier: `hermes-setup-gated`
Reasoning demand: `light`

Quality bar:

- Prerequisite check: confirm the subscription, account, or capability the step needs exists before continuing; mark unmet prerequisites "not applicable" and skip them explicitly.
- Read-only diagnose: read the current Hermes config, `.env` keys, and installed version without writing anything.
- Guide: walk the user through any account creation, OAuth, or token issuance they must complete themselves.
- Diff-approved apply: show the exact config or `.env` diff and write only after the user explicitly approves it.
- Verify: re-read the updated config and report a completion checklist covering every applicable item.
- This is mostly a verify-only walkthrough: prefer reporting capability status over proposing a config change when parallel tools are already current.

Handoff policy:

Run diagnosis and reporting directly in Hermes for parallel-tool capability. Diagnosis only reads the existing Hermes config, `.env` keys, and installed version; it never writes anything on its own. Show the exact diff for any config or `.env` change and write it only after the user explicitly approves that diff. Secret values such as tokens and API keys are pasted by the user directly in chat and are never stored, logged, or echoed back beyond the immediate diff confirmation. Delegate to a selected coding executor only if the user needs a change outside a local version/config check.

Required inputs:

- installed Hermes version
- current parallel-tool capability status

Expected outputs:

- read-only diagnosis of the installed version and parallel-tool capability status
- a user-runnable update command to check or restore version currency
- a capability status report naming which parallel-tool features are active

Artifact expectations:

- capability status note when the wrapper captures it

Safety rules:

- Do not name a specific version number, release date, or product tier; read and report the installed version instead of assuming one.
- Report the update command for the user to run themselves rather than claiming Hermes restarted or reloaded on its own.

## Runtime Evidence

Preferred harness for this skill: `coding-handling`.

```sh
omh runtime record --skill parallel-tools --harness coding-handling --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
