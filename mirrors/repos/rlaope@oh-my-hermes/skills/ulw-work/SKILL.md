---
name: ulw-work
description: [omh] Ultrawork - split an accepted plan into disjoint parallel lanes with per-lane acceptance criteria, verification commands, and owners; prevents two lanes editing the same file. Aliases: ulw. Use when the user says: ultrawork, parallel work, parallel implementation, high throughput.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, execution]
    category: execution
    phase: parallel-delivery
    role: handoff-guide
    quality_tier: handoff-gated
---

# Ultrawork

This is a Hermes-native `ultrawork` workflow skill.

## Why This Exists

`ultrawork` exists to split an accepted implementation plan into independent lanes without letting parallelism blur ownership, verification, worker protocol, worktree isolation, or observed runtime evidence.

## Do Not Use When

- The work touches the same files or invariants in ways that need one owner.
- The plan is not accepted, lane boundaries are unclear, or verification commands are missing.
- The user expects Hermes to secretly execute coding lanes instead of preparing explicit selected-runtime handoffs.
- The lanes are exploratory research or QA coordination without an accepted implementation plan; use `team`.
- The request is a settings-only change, one bounded edit that is explicitly low-risk and has a direct owner and verification path, or a direct answer/diagnosis; use one direct owner instead of opening parallel delivery lanes.

## Examples

Good example:

- Prompt: $ultrawork split the accepted docs refresh, CLI output polish, and test updates into parallel implementation lanes.
- Expected behavior: Create disjoint lane prompts with acceptance criteria, verification commands, and review evidence requirements.
- Why: The work can be split cleanly and benefits from parallel execution discipline.

Bad example:

- Prompt: $ultrawork refactor the central router in five agents at once.
- Expected behavior: Keep one owner or re-plan boundaries before parallelization.
- Why: Shared core logic makes parallel edits likely to conflict or hide regressions.

## Completion Checklist

- All work lanes are disjoint by file, invariant, or responsibility before preparing parallel handoffs.
- Each lane has acceptance criteria, verification command, worker protocol expectation, and review owner.
- When Hermes owns the coding path, use `hermes_coding_harness/v1` to separate builder, verifier, reviewer, docs, and PR lanes.
- Worker ACK, dispatch, result, review, CI, and merge evidence are observed or explicitly missing.
- Integration verification ran after lane results before the final status claims completion.

## Recovery Notes

- If lanes are non-disjoint, collapse to one owner or route back to ultragoal before coding starts.
- If a worker does not ACK or return a result, keep that lane blocked/not_observed and expose the retry or reassignment action.
- If a worktree or shared-file conflict appears, pause parallel delivery and re-plan ownership before more edits.

## Workflow Lane

- Current lane: **Coding handoff** (`idea-to-deploy`, `cto-loop`, `deploy-and-monitor`, `code-review`, `build-failure-triage`, `verification-gate`, `security-safety-review`, `ultrawork`, `+7 more`) - coding owners, handoffs, review, CI, and merge evidence.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when an accepted implementation plan can be split into independent, reviewable work lanes.

    Strong routing signals: `ultrawork`, `$ultrawork`, `ulw`, `$ulw`, `parallel work`, `parallel implementation`, `high throughput`

## Catalog Metadata

Category: `execution`
Phase: `parallel-delivery`
Hermes role: `handoff-guide`
Quality tier: `handoff-gated`
Reasoning demand: `heavy`

Quality bar:

- Do not start this engine as an automatic continuation of another skill's output: an accepted plan, a clarified brief, or a routing recommendation is planning evidence, not permission. Unless the user explicitly invoked this engine themselves, restate in one line what will start (engine, scope, selected executor) and wait for the user's explicit go-ahead first.
- Require disjoint lane ownership before preparing multiple coding runtime handoffs.
- Attach acceptance criteria, verification commands, and review expectations to each lane.
- Keep dispatch, execution, review, CI, and merge status evidence separate.

Handoff policy:

Keep the workflow name for compatibility, but convert coding lanes into explicit selected runtime handoffs with disjoint scope, verification, review evidence, worker protocol, and worktree guidance.

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

- accepted plan
- lane list
- disjoint file or responsibility scopes
- verification commands

Expected outputs:

- runtime handoff prompts or lane instructions
- status summary
- review/CI evidence requirements

Artifact expectations:

- prepared coding delegation record per implementation lane when wrappers can record them

Safety rules:

- Do not start parallel coding without disjoint ownership boundaries.
- Keep Hermes responsible for orchestration/status; when Hermes itself is selected for coding, still preserve runtime evidence boundaries.
- Record unobserved executor work as prepared_not_observed or not_observed.

## Runtime Evidence

Preferred harness for this skill: `goal-execution`.

```sh
omh runtime record --skill ultrawork --harness goal-execution --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- When wrapper metadata includes `memory_review_card/v1` or `handoff_context_pack/v1`, treat it as reviewed OMH-local or wrapper-supplied context only. Use conflict-free context summaries to shape plans and handoffs, but do not claim Hermes internal memory was read or changed.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
