---
name: ulw-process
description: [omh] Ultraprocess - one full task-to-PR cycle: codebase research, reviewed plan, coding handoff to the selected executor, code review, docs sync, and PR, tracked end to end. Aliases: ulp. Use when the user says: ultraprocess, single-cycle delivery, one-cycle delivery, end-to-end process, delivery process, research plan implement review docs pr, plan implement review docs pr, ralplan ultragoal code-review.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, process]
    category: process
    phase: single-cycle-plan-to-pr
    role: handoff-guide
    quality_tier: process-gated
---

# Ultraprocess

This is a Hermes-native `ultraprocess` workflow skill.

## Why This Exists

`ultraprocess` exists to give Hermes one clean plan-to-PR operating cycle: research, reviewed plan, selected implementation handoff, review gate, docs sync, and PR-ready evidence.

## Do Not Use When

- The user wants an open-ended feedback loop or long-horizon campaign; use `loop` instead.
- The task is still ambiguous enough that a deep interview is required before planning.
- No repo, product, or delivery surface is available to support a plan-to-PR cycle.
- The goal is removing existing slop or duplication with identical observable behavior rather than delivering new or changed behavior; use `ai-slop-cleaner`.
- The request starts with product shaping and explicitly includes release, deploy, or monitor decisions beyond one PR; use `idea-to-deploy`.
- The request is a settings-only change, one bounded edit that is explicitly low-risk and has a direct owner and verification path, or a direct answer/diagnosis; handle it directly instead of starting a plan-to-PR cycle.

## Examples

Good example:

- Prompt: $ultraprocess research this setup bug, plan the fix, implement, review, sync docs, and prepare a PR.
- Expected behavior: Run exactly one delivery cycle and report which stages are observed, prepared, or blocked.
- Why: The user explicitly asks for the full but bounded delivery path ending at PR readiness.

Bad example:

- Prompt: $ultraprocess keep improving the project until it becomes popular.
- Expected behavior: Route to `loop` or ask for a bounded goal rather than promise endless delivery.
- Why: Popularity and indefinite improvement need long-horizon loop management, not one PR-ready cycle.

## Completion Checklist

- Research and codebase context are captured before implementation handoff.
- A ralplan-style or reviewed plan names acceptance criteria, risks, and verification commands.
- The implementation owner is selected and handoff, dispatch, run, review, CI, and PR readiness are separated.
- If the implementation owner is Hermes, `hermes_coding_harness/v1` names the current stage, lane owner, next action, and missing evidence.
- The code-review gate is observed or explicitly marked not_observed.
- Docs sync is checked when behavior, setup, commands, examples, or public claims changed.

## Recovery Notes

- If the task expands beyond one delivery cycle, stop and route to loop with the current evidence as input.
- If no implementation owner is selected, keep the work prepared_not_observed and ask for Codex, Claude Code, Hermes, or another runtime.
- If review, CI, docs sync, or PR evidence is missing, report the stage gap instead of saying the process is complete.

## Workflow Lane

- Current lane: **Intent -> plan** (`oh-my-hermes`, `meta-router`, `deep-interview`, `context`, `plan`, `ralplan`, `codebase-onboarding`, `codegraph-refresh`, `+7 more`) - clarify, plan, ship, or loop goals.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when the user asks Hermes to take a concrete task through one full delivery cycle: research/codebase context, reviewed plan, selected implementation handoff, code review, docs sync when needed, and PR preparation.

    Strong routing signals: `ultraprocess`, `$ultraprocess`, `ulp`, `$ulp`, `./ultraprocess`, `/ultraprocess`, `single-cycle delivery`, `one-cycle delivery`, `end-to-end process`, `delivery process`, `research plan implement review docs pr`, `plan implement review docs pr`, `ralplan ultragoal code-review`, `codebase source research planning implementation review docs sync pr`, `docs sync`, `pr-ready`, `prepare a pr`, `sync docs and prepare a pr`, `code-review sync docs and prepare a pr`, `delegate to codex`, `send to codex`, `codex implement`, `codex progress tracking`, `codex session tracking`, `make a pr`, `open a pr`, `끝까지 해줘`, `PR까지`, `계획 구현 리뷰 문서 PR`, `기획 구현 리뷰 문서 PR`, `코드베이스 조사 웹리서치 계획 구현 리뷰 문서 최신화 PR`, `codex로 구현`, `코덱스로 구현`, `codex에게 맡기`, `codex로 맡기`, `코덱스에게 맡기`, `코딩 에이전트에게 맡기`, `구현하게 맡기고 진행상태 추적`, `진행상태 추적`, `진행 상태 추적`, `문서 최신화 PR`, `test driven development`, `write tests first`, `tests first`, `tdd implementation`, `테스트부터 작성`, `테스트 먼저 작성`, `테스트 우선 구현`, `TDD로 구현`

## Catalog Metadata

Category: `process`
Phase: `single-cycle-plan-to-pr`
Hermes role: `handoff-guide`
Quality tier: `process-gated`
Reasoning demand: `heavy`

Quality bar:

- Do not start this engine as an automatic continuation of another skill's output: an accepted plan, a clarified brief, or a routing recommendation is planning evidence, not permission. Unless the user explicitly invoked this engine themselves, restate in one line what will start (engine, scope, selected executor) and wait for the user's explicit go-ahead first.
- Complete exactly one plan-to-PR delivery cycle, then stop with status, evidence gaps, or a next recommended workflow.
- Start with codebase/source research and a ralplan-style decision record before implementation handoff.
- For implementation, hand off to ultragoal or the selected executor/runtime path with acceptance criteria and verification commands attached, and start that follow-on engine only after the user confirms the recommended path.
- Run code-review as a gate after implementation evidence exists; review preparation alone is not review evidence.
- Add docs-specialist sync when public behavior, commands, setup, examples, or claims changed.
- End with a PR-ready or PR-observed report that separates prepared, executed, reviewed, verified, CI, and PR evidence.

Handoff policy:

Keep the one-cycle process orchestration, source/codebase research, planning, review framing, docs-sync checks, PR narration, and evidence boundaries in Hermes; convert implementation into a selected executor/runtime handoff such as Codex, Claude Code, OMX/OMO/OMC, another coding agent, or explicit Hermes coding runtime only when the user accepts that owner.

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

- task statement
- repo or workspace context
- executor preference or choose-at-handoff policy
- verification expectations

Expected outputs:

- ralplan-ready context and plan
- ultragoal or selected executor/runtime handoff
- code-review gate
- docs sync checklist
- single-cycle PR-ready summary with observed evidence and gaps

Artifact expectations:

- process checklist or runtime record when a wrapper can observe the stages
- prepared handoff artifact only after implementation owner selection
- docs-specialist claim check when public behavior changes

Safety rules:

- Do not skip planning when the request is broad, risky, or user-visible.
- Do not continue into a repeated feedback loop; recommend `loop` when the user wants ongoing cycles.
- Do not claim implementation, review, CI, merge readiness, or PR creation without observed executor or GitHub evidence.
- Keep web research source-backed and permission-aware; do not run hidden network or LLM calls from OMH core.
- Run docs sync only when behavior, setup, commands, or public claims changed.

## Runtime Evidence

Preferred harness for this skill: `goal-execution`.

```sh
omh runtime record --skill ultraprocess --harness goal-execution --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- When wrapper metadata includes `memory_review_card/v1` or `handoff_context_pack/v1`, treat it as reviewed OMH-local or wrapper-supplied context only. Use conflict-free context summaries to shape plans and handoffs, but do not claim Hermes internal memory was read or changed.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
