---
name: ulw-team
description: [omh] Team - run N coordinated workers on one shared task list with explicit lane ownership and merged verification; choose over raw subagents when lanes must not collide. Use when the user says: team, swarm, parallel agents, coordinated workers.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, execution]
    category: execution
    phase: coordination
    role: handoff-guide
    quality_tier: coordination-gated
---

# Team

This is a Hermes-native `team` workflow skill.

## Why This Exists

`team` exists to keep `execution` work explicit, evidence-backed, and inside the Hermes/executor boundary instead of relying on ad hoc chat narration.

## Do Not Use When

- An accepted implementation plan with disjoint files, criteria, and commands is ready for parallel delivery; use `ultrawork`.
- The request is a settings-only change, one bounded edit that is explicitly low-risk and has a direct owner and verification path, or a direct answer/diagnosis; use one direct owner instead of coordinating workers.

## Examples

Good example:

- Prompt: team: coordinate parallel agents for frontend polish, copy polish, and QA with worker ACKs.
- Expected behavior: Assign lanes, require worker ACK/result evidence, and keep integration verification separate.
- Why: The work benefits from multiple coordinated workers with disjoint ownership.

Bad example:

- Prompt: team: treat casual chat or unaccepted work as if this workflow already produced verified results.
- Expected behavior: Ask a clarification question or route to a narrower workflow instead of forcing `team`.
- Why: The request lacks the required inputs or would overclaim work that Hermes did not observe.

## Completion Checklist

- Each lane has an owner, disjoint scope, expected output, and verification target.
- Worker ACK, dispatch, result, integration, and verification evidence are separated when wrappers record them.
- Hermes-owned coding teams use `hermes_coding_harness/v1` so builder, verifier, reviewer, docs, and PR lanes stay distinct even in solo mode.
- The integrated status names which lanes are observed, blocked, or still prepared_not_observed.

## Recovery Notes

- If two lanes are not independent, collapse them under one owner or re-plan before dispatch.
- If a worker has no ACK or result, mark that lane not_observed or blocked rather than infer progress.
- If integration reveals a shared-file conflict, stop lane fan-out and reassign ownership before continuing.

## Workflow Lane

- Current lane: **Coding handoff** (`idea-to-deploy`, `cto-loop`, `deploy-and-monitor`, `code-review`, `build-failure-triage`, `verification-gate`, `security-safety-review`, `ultrawork`, `+7 more`) - coding owners, handoffs, review, CI, and merge evidence.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when multiple independent lanes materially improve throughput or verification.

    Strong routing signals: `team`, `$team`, `swarm`, `parallel agents`, `coordinated workers`

## Catalog Metadata

Category: `execution`
Phase: `coordination`
Hermes role: `handoff-guide`
Quality tier: `coordination-gated`
Reasoning demand: `heavy`

Quality bar:

- Do not start this engine as an automatic continuation of another skill's output: an accepted plan, a clarified brief, or a routing recommendation is planning evidence, not permission. Unless the user explicitly invoked this engine themselves, restate in one line what will start (engine, scope, selected executor) and wait for the user's explicit go-ahead first.
- Split only independent lanes with explicit ownership and verification boundaries.
- Keep Hermes as coordinator and status narrator while coding lanes become runtime handoffs with explicit ownership.
- Integrate lane evidence before reporting combined progress.

Handoff policy:

Use Hermes for lane framing and status; implementation lanes should become selected runtime handoff tasks, including Hermes-owned coding when the user chooses that runtime.

Executor readiness:

- When accepted work mutates code, check `executor_readiness/v1` for the selected Codex, Claude Code, Hermes, or oh-my runtime path before first dispatch.
- If readiness is `missing` or `blocked`, ask the user to choose another coding agent, configure PATH, continue in Hermes, or keep a prompt/runtime handoff; retry only after that state changes.
- A readiness probe is not dispatch, implementation, verification, review, CI, merge-readiness, or merge evidence.

Delegation transparency:

- When delegating, show the composed delegate prompt in a fenced code block in the status message; truncate a long prompt to a bounded preview ending with `... [truncated, N chars total]` — the user must see WHAT was asked, not just that something was.
- Name every delegated or parallel lane's model and reasoning effort inline as `(model effort)` in status and briefing lines — including runtime-native subagents; write the literal `unknown` when the host does not expose a value, never empty parentheses, and carry token and elapsed figures the same way.
- Capture a resumable session or thread id at dispatch and report it in the status message: for non-interactive Claude Code pass `--output-format json` and read `session_id` from the result (resume with `claude -p --resume <session-id>`); for Codex pass `--json` and read `thread_id` (resume with `codex exec resume <thread-id>`, repeating `--skip-git-repo-check` outside a git repo). Never leave a delegate run with no recorded way to resume or steer it — a plain-text one-shot that hides its session id strands the work when the run stalls or times out.
- Before dispatch, grant the executor session every permission the task will need — file write/edit, command/test execution, and the working directory — on the dispatch command itself, not through settings-file guesses: for non-interactive Claude Code pass `--permission-mode acceptEdits` or an explicit `--allowedTools` list (`--dangerously-skip-permissions` only inside an isolated worktree or sandbox), and the equivalent sandbox/approval flags for other CLIs. `acceptEdits: true` is not a settings key and `~/.claude/settings.local.json` is not a file Claude Code reads — user scope is `~/.claude/settings.json` and project scope is `<dispatch cwd>/.claude/settings.local.json` with rules under `permissions.allow`. Prove the grant with a bounded scratch-edit probe run before the real dispatch: a permission denial in a non-interactive run recurs identically on retry, so never redispatch until a changed grant is proven, and surface an ungrantable permission as a blocker before dispatch, not after minutes of silence.

Required inputs:

- bounded lane definitions
- ownership boundaries
- verification target

Expected outputs:

- lane results
- integration summary
- combined verification evidence

Artifact expectations:

- delegation record only when separate participants are observed

Safety rules:

- Use parallel lanes only when work is independent.
- Keep shared-file edits under one owner.
- Record unobserved delegation as not_observed.

## Runtime Evidence

Preferred harness for this skill: `goal-execution`.

```sh
omh runtime record --skill team --harness goal-execution --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- When wrapper metadata includes `memory_review_card/v1` or `handoff_context_pack/v1`, treat it as reviewed OMH-local or wrapper-supplied context only. Use conflict-free context summaries to shape plans and handoffs, but do not claim Hermes internal memory was read or changed.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
