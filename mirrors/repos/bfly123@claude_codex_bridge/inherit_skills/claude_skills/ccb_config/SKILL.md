---
name: ccb_config
description: Design and edit CCB project teams by updating .ccb/ccb.config plus shared and per-agent memory. Use when the user wants to add, rename, remove, or reorganize CCB agents; choose providers, worktree isolation, models, API shortcuts, or workflow roles; or turn a natural-language team/workflow description into a valid CCB config.
---

# CCB Config

Use this skill to design and edit a CCB-managed project team. The usual output is a valid `.ccb/ccb.config` plus preserved project memory updates in `.ccb/ccb_memory.md` and `.ccb/agents/<agent>/memory.md`. If the user explicitly asks for a user-level default team, edit `~/.ccb/ccb.config` instead.

## Core Workflow

1. Resolve the config authority first. CCB config precedence is built-in default < user config `~/.ccb/ccb.config` < project config `.ccb/ccb.config`. `.ccb_config/ccb.config` is legacy residue and must be treated as read-only migration evidence, not as the file to edit.
2. Read the current `.ccb/ccb.config`, `.ccb/ccb_memory.md`, and relevant `.ccb/agents/<agent>/memory.md` files before proposing changes.
3. If the user's project goal and workflow are not already clear, ask a short clarification question before designing the team.
4. After the basic workflow is clear, propose one complete config with sensible defaults and ask for confirmation or adjustments.
5. Prefer compact or hybrid config for ordinary single-window teams. Existing compact/hybrid configs stay single-window and should not be migrated to `[windows]` unless the user wants named tmux windows, multi-window sidebar layout, or per-window agent grouping.
6. When the user asks to modernize, split, or reorganize an old config, treat it as a migration task: preserve the old roster and overrides by default, propose the new target shape, then write only after confirmation.
7. Edit only user-authored authority files:
   - `.ccb/ccb.config`
   - `.ccb/ccb_memory.md`
   - `.ccb/agents/<agent>/memory.md`
8. Validate the written config with the CCB config loader and verify that the loader read the intended source kind.
9. Tell the user that CCB must be restarted for config changes to take effect.

Do not write runtime state, generated memory, provider-state homes, `.ccb/provider-profiles/`, `.ccb/ccbd/`, legacy `.ccb_config/`, or provider-native project dotfiles such as `.codex`, `.claude`, or `.gemini`.

By default, configure the current project by writing `.ccb/ccb.config`. Only write `~/.ccb/ccb.config` when the user explicitly asks for a user-level or system-wide default CCB team.

Never run `ccb`, `ccb -s`, `ccb kill`, or any restart command as part of this skill workflow. Restarting from inside an active CCB pane can terminate the current session before file edits and validation finish. Finish all file writes and validation first, then tell the user the restart command to run manually.

## Interaction Pattern

Use a clarify, propose, confirm flow. Do not interrogate the user with a long questionnaire, and do not jump straight to a roster when the project purpose is unknown.

First ask for the minimum context needed to design a useful team. Prefer one compact question with 2-3 parts:

```text
What is this project/workflow mainly for, and do you expect parallel implementation work? I can default to a light team unless you want multiple workers or separate discussion/review agents.
```

Ask about these basics, but only when they are not already clear from the user's request or existing project files:

- project purpose or workflow: coding product, library maintenance, research, docs, QA, release, operations, discussion-heavy planning, etc.;
- whether the team should support parallel execution or mostly serial coordination; if parallel execution is requested and no worker count is given, default to 3 implementation workers;
- whether workers should edit code in isolated git worktrees or stay `inplace`;
- whether providers should inherit the system provider setup or use explicit per-agent API/model overrides.

Do not ask a separate question for every agent. Infer role names, worker count, providers, worktree policy, and layout from the project purpose and the user's answer. Then present one concrete proposal with defaults and invite edits.

Second, propose a complete draft:

```text
I will configure:
- main: planning, task sequencing, and delegation
- worker1: implementation in a git worktree
- reviewer: review and risk checks

Config:
cmd; main:codex, worker1:codex(worktree); reviewer:claude

Defaults:
- providers inherit the system setup
- restore stays auto
- permission stays manual
- no separate API keys or models

Confirm this, or tell me what to change.
```

Default proposal shape:

```text
cmd; main:codex, worker1:codex(worktree); reviewer:claude
```

Full proposal shape for parallel implementation:

```text
cmd; main:codex, worker1:codex(worktree), worker2:codex(worktree), worker3:claude(worktree); reviewer:claude, discuss:codex
```

Only write files after the user confirms the proposed design or explicitly asks you to apply it.

Only ask additional questions when a safe default does not exist, for example:

- The user requires isolated workspaces in a non-git project.
- The user asks for separate API credentials but has not provided or named the credential source.
- The user requests a provider/model not supported by the current CCB installation.
- Renaming/removing an existing agent would leave old memory files whose fate is ambiguous.

## Migration Tasks

Use this flow when the user asks to convert an existing compact/hybrid config to a newer layout, add multiple windows, add sidebars, or reorganize agents by window:

1. Read the current config and identify whether it is compact, hybrid, explicit windows, or legacy rich TOML.
2. Preserve existing agent names, providers, `(worktree)` markers, models, keys, urls, descriptions, labels, permissions, restore settings, provider profiles, and memory files unless the user asks to change them.
3. If the user wants to stay single-window, keep compact/hybrid format and only adjust the compact layout or overlay fields.
4. If the user wants multi-window, named windows, or per-window sidebar layout, migrate to `version = 2` with `[windows]`.
5. In `[windows]`, remove `cmd`; a persistent `cmd` pane is a compact/hybrid feature.
6. Keep each agent in exactly one window. Use window names that match the workflow, such as `main`, `work`, `review`, `research`, or `ops`.
7. Move agent-specific extras into `[agents.<name>]` tables after the `[windows]` block.
8. Present a before/after proposal and ask for confirmation before writing.

Example migration:

```text
Before:
cmd; main:codex, worker1:codex(worktree), worker2:claude(worktree); reviewer:claude

After:
version = 2
entry_window = "main"

[windows]
main = "main:codex"
work = "worker1:codex(worktree), worker2:claude(worktree)"
review = "reviewer:claude"
```

## Defaults

- Keep `cmd` enabled unless the user explicitly disables it.
- Use `main` as the coordinator for planning, progress, and delegation.
- Use one worker for small projects or serial workflows.
- Use 3 implementation workers when the user wants parallel execution but does not specify a worker count.
- Use worktree isolation for implementation workers in git repositories: `worker1:codex(worktree)`.
- Use `inplace` for `main`, `reviewer`, and `discuss` unless the user asks for isolation.
- Inherit provider credentials/config by default. Do not write `key`, `url`, `provider_profile`, or API env unless explicitly requested.
- Keep `restore = "auto"`, `permission = "manual"`, `runtime_mode = "pane-backed"`, and `queue_policy = "serial-per-agent"` unless the user explicitly asks otherwise.
- Add `description` fields only when useful; do not add verbose config metadata when memory files already carry the role guidance.

## Config Knowledge

Read `references/ccb-config.md` when editing `.ccb/ccb.config` or explaining syntax.

Key points:

- Compact agent leaves must be `agent:provider` or `agent:provider(worktree)`.
- `cmd` is a layout keyword, not an agent, and must not have a provider or `[agents.cmd]` table.
- `;` creates horizontal columns from left to right.
- `,` creates vertical rows within a column from top to bottom.
- In compact/hybrid config, the first compact block owns layout, default agents, cmd, provider, and workspace mode.
- Compact/hybrid config without `[windows]` is a legacy-compatible single-window layout even when CCB supports windows topology.
- Hybrid TOML overlay may only add fields for agents already declared in the compact header and must not redefine `provider` or `workspace_mode`.
- Explicit windows topology uses `version = 2`, `[windows]`, and optional `[ui.sidebar]`; it must not include `default_agents`, `layout`, or `cmd_enabled`.
- `cmd` is not supported inside `[windows]` topology. Use compact/hybrid config when a persistent command pane is required.
- Migration to `[windows]` is opt-in and should preserve existing agent fields unless the user asks for role/provider/workspace changes.
- `agent:provider(worktree)` maps to `workspace_mode = "git-worktree"`.
- `git-worktree` requires the project root to be a git repository; CCB must not silently fall back to copying.

## Memory Updates

Read `references/memory-patterns.md` before writing role memory.

Rules:

- Preserve user-authored content.
- Prefer replacing a marked CCB role block over appending duplicates.
- Do not edit generated runtime memory files.
- Keep role memory direct and operational, not promotional.
- For `main`, include that tasks should be split into large coherent chunks, not tiny fragments, because workers are full agents with their own planning and implementation ability.
- For parallel workflows, describe parallel work as separate root work packages. Do not imply that one active task can fan out to multiple callback dependencies and then fan in automatically.
- Prefer direct owner-to-next-owner handoffs such as `main -> worker -> reviewer` when the next result is needed, using `ask --callback` at each active dependency step.

Shared memory block marker:

```md
<!-- CCB-WORKFLOW-START -->
...
<!-- CCB-WORKFLOW-END -->
```

Per-agent memory block marker:

```md
<!-- CCB-ROLE-START -->
...
<!-- CCB-ROLE-END -->
```

If an existing marker is present, replace only that block. If not, append the new block after existing content. Create missing per-agent memory files as needed.

## Validation

After editing `.ccb/ccb.config`, run:

```bash
python - <<'PY'
from pathlib import Path
from agents.config_loader import load_project_config
result = load_project_config(Path('.'))
if result.source_kind != 'project_config' or result.source_path is None:
    raise SystemExit('ERROR: .ccb/ccb.config was not loaded; write the current config authority before validating')
print(f'{len(result.config.agents)} agents OK: {", ".join(result.config.default_agents)}')
PY
```

After editing `~/.ccb/ccb.config` as the user-level default, validate from a temporary directory without a project config and require `source_kind == "user_config"`.

Also check:

- agent names are valid and not reserved;
- compact/hybrid config: every configured default agent appears exactly once in the layout and `cmd` is first when enabled;
- windows topology config: every configured agent appears in exactly one `[windows]` layout and no `cmd` leaf is present;
- compact/hybrid worktree markers are present on the compact line, not in overlay;
- validation reports the intended `source_kind` and a non-empty `source_path`;
- no secrets were added unless the user explicitly provided them;
- memory updates preserved existing unmarked content.

## Boundaries

- Do not bootstrap a new `.ccb/ccb.config` without user confirmation.
- Never write `.ccb_config/ccb.config`; if it exists, treat it as legacy residue only.
- Do not delete memory files for removed agents unless the user explicitly asks.
- Do not create or edit provider profile directories directly.
- Do not change runtime state to "apply" a config; do not run `ccb`, `ccb -s`, `ccb kill`, or restart from inside the skill; tell the user to restart CCB after the skill has finished.
- Do not use `workspace_mode = "copy"` unless the user explicitly chooses copy workspace behavior.
