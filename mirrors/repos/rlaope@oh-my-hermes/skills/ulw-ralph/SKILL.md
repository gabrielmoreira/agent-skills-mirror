---
name: ulw-ralph
description: [omh] Ralph - one owner drives a concrete task to done: implement, verify, review, repeat until the gate passes; prefer over one-shot delegation when the task needs a verification loop. Aliases: ulr. Use when the user says: ralph, finish until done, persistent execution, self-referential loop.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, execution]
    category: execution
    phase: completion
    role: handoff-guide
    quality_tier: handoff-gated
---

# Ralph

This is a Hermes-native `ralph` workflow skill.

## Why This Exists

`ralph` exists to keep `execution` work explicit, evidence-backed, and inside the Hermes/executor boundary instead of relying on ad hoc chat narration.

## Do Not Use When

- Progress must survive sessions as a ledger with multiple checkpoints and a final gate; use `ultragoal`.
- The request is a settings-only change, one bounded edit that is explicitly low-risk and has a direct owner and verification path, or a direct answer/diagnosis; handle it directly instead of opening a finish-until-done loop.

## Examples

Good example:

- Prompt: ralph: finish the invoice export recovery until the smoke test passes or a blocker is recorded.
- Expected behavior: Keep one completion owner, track evidence after every recovery step, and stop only on pass, block, or explicit cancel.
- Why: The request needs persistent completion pressure with an observable stop condition.

Bad example:

- Prompt: ralph: treat casual chat or unaccepted work as if this workflow already produced verified results.
- Expected behavior: Ask a clarification question or route to a narrower workflow instead of forcing `ralph`.
- Why: The request lacks the required inputs or would overclaim work that Hermes did not observe.

## Completion Checklist

- The selected coding or runtime owner is named before any implementation claim.
- Prepared handoff, dispatch, execution, verification, review, CI, and merge states are separated.
- The final status cites observed runtime evidence or keeps the work prepared_not_observed.
- When Hermes is the selected coding owner, use `hermes_coding_harness/v1` to keep builder, verifier, reviewer, docs, and PR lanes separate.
- Report the current harness stage, owner, next action, and missing evidence without claiming PR creation, review, CI, merge-readiness, or merge until matching runtime observations exist.

## Recovery Notes

- If the selected executor is unavailable, ask for Codex, Claude Code, Hermes, or another runtime before retrying.
- If dispatch or result evidence is missing, keep the handoff prepared_not_observed and expose the next observable action.

## Workflow Lane

- Current lane: **Intent -> plan** (`oh-my-hermes`, `meta-router`, `deep-interview`, `context`, `plan`, `ralplan`, `codebase-onboarding`, `codegraph-refresh`, `+7 more`) - clarify, plan, ship, or loop goals.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use after scope is concrete and the user wants one owner to continue through implementation and verification.

    Strong routing signals: `ralph`, `$ralph`, `ulr`, `$ulr`, `finish until done`, `persistent execution`, `self-referential loop`

## Catalog Metadata

Category: `execution`
Phase: `completion`
Hermes role: `handoff-guide`
Quality tier: `handoff-gated`
Reasoning demand: `heavy`

Quality bar:

- Do not start this engine as an automatic continuation of another skill's output: an accepted plan, a clarified brief, or a routing recommendation is planning evidence, not permission. Unless the user explicitly invoked this engine themselves, restate in one line what will start (engine, scope, selected executor) and wait for the user's explicit go-ahead first.
- Do not enter a finish-until-done loop until scope, acceptance criteria, and verification commands are concrete.
- For coding edits, prepare and track selected runtime evidence instead of implying unobserved work happened.
- Report completion only from observed execution and verification evidence.

Handoff policy:

Keep as compatibility guidance; for implementation, ask the wrapper to prepare/track the selected coding runtime path instead of hiding execution inside chat narration.

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

- concrete scope
- acceptance criteria
- verification commands

Expected outputs:

- completed work summary
- verification evidence
- remaining risks

Artifact expectations:

- goal-execution run record
- checkpoint or final evidence when available

Safety rules:

- Do not imply hidden Hermes runtime behavior.
- Use the smallest verification that can prove the claim.

## Runtime Evidence

Preferred harness for this skill: `goal-execution`.

```sh
omh runtime record --skill ralph --harness goal-execution --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- When wrapper metadata includes `memory_review_card/v1` or `handoff_context_pack/v1`, treat it as reviewed OMH-local or wrapper-supplied context only. Use conflict-free context summaries to shape plans and handoffs, but do not claim Hermes internal memory was read or changed.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
