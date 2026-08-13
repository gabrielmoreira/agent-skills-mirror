---
name: omh-terminal
description: [omh] Policy overlay for terminal commands - add cwd, environment, safety, and result-evidence gates after preferring native shell tools for ordinary CLI, package-manager, and test runs. Use when the user says: command-operator, command operator, terminal command, terminal task, shell command, shell task, cli command, command execution.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, command]
    category: command
    phase: command-task
    role: guide
    quality_tier: workflow-surface-gated
---

# Command Operator

This is a Hermes-native `command-operator` workflow skill.

## Why This Exists

`command-operator` exists so Hermes users can ask for this workflow in chat and receive a structured, evidence-bounded OMH operating surface instead of ad hoc narration.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: command-operator run npm test in the project terminal and summarize the output.
- Expected behavior: Produce `prepare_command_operator_card` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: command-operator run rm -rf without cwd, confirmation, or observation gates.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMH guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- Command text, working directory, environment assumptions, timeout, safety level, and stop condition are explicit.
- Destructive, credential, network, filesystem mutation, install, deploy, and production commands are gated or marked missing.
- Exit codes, stdout/stderr, test results, package-manager effects, and filesystem mutations are reported only from observed command evidence.

## Recovery Notes

- If command text or working directory is missing, ask for the smallest missing scope needed before preparing the command task.
- If the command is destructive, credentialed, networked, install/deploy-oriented, or production-affecting, require an explicit confirmation gate.
- If the user supplied failed command output and asks for root cause, route to build-failure-triage or agent-debug instead of preparing a fresh command.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `buzz`, `agent-board`, `gateway-intent-card`, `+34 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when Hermes should prepare or supervise terminal/CLI command execution without claiming the command ran or succeeded.

    Strong routing signals: `command-operator`, `command operator`, `terminal command`, `terminal task`, `shell command`, `shell task`, `cli command`, `command execution`, `run command`, `run this command`, `execute command`, `execute this command`, `run npm test`, `run tests`, `npm test`, `pnpm test`, `bun test`, `uv run`, `python -m unittest`, `pytest`, `make test`, `cargo test`, `go test`, `summarize command output`, `터미널 명령`, `터미널에서`, `셸 명령`, `쉘 명령`, `명령 실행`, `명령어 실행`, `실행 준비`, `npm test 실행`, `테스트 실행`, `결과 요약`

## Catalog Metadata

Category: `command`
Phase: `command-task`
Hermes role: `guide`
Quality tier: `workflow-surface-gated`
Reasoning demand: `standard`

Quality bar:

- Name the user-facing workflow objective, required context, next action, and stop condition.
- Separate prepared guidance from observed platform, runtime, connector, file, memory, or delivery evidence.
- Expose missing tools, credentials, targets, or observations as user-visible gaps.

Handoff policy:

Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded.

Required inputs:

- user request
- target context
- delivery or status expectation
- known missing evidence

Expected outputs:

- command_task_card/v1
- command_scope/v1
- command_safety_gate/v1
- command_result_manifest/v1 when observed
- next action
- prepared-vs-observed boundary

Artifact expectations:

- command_task_card/v1 metadata-only wrapper card when prepared
- command_scope/v1 with command text, working directory, environment assumptions, timeout, and stop condition
- command_safety_gate/v1 separating read-only, write/mutation, network, credential, and destructive-risk commands
- command_result_manifest/v1 only when exit code, stdout/stderr, logs, or terminal transcript are observed

Safety rules:

- A command operator card is not terminal launch, shell execution, package-manager action, test run, stdout/stderr capture, exit-code success, filesystem mutation, network access, or destructive command evidence unless observed command-result evidence records it.
- Do not claim connector, gateway, runtime, file generation, memory mutation, or host automation evidence from prepared guidance.

## Runtime Evidence

Preferred harness for this skill: `command-operator`.

```sh
omh runtime record --skill command-operator --harness command-operator --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
