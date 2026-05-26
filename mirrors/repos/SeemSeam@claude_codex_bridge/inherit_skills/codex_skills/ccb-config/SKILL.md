---
name: ccb-config
description: Design, edit, or migrate CCB project teams by updating .ccb/ccb.config. Use when the user wants to add, rename, remove, or reorganize CCB agents; choose providers, worktree isolation, models, API shortcuts, single-window or multi-window layout; migrate an old ccb.config to the current windows topology; handle optional skill inheritance or injection requests for agents; or turn a natural-language team/workflow description into a valid CCB config. Only update shared or per-agent memory when the user explicitly asks for workflow memory design.
---

# CCB Config

Use this skill to design, edit, or migrate a CCB-managed project team. The usual output is a valid `.ccb/ccb.config`. Do not edit `.ccb/ccb_memory.md` or `.ccb/agents/<agent>/memory.md` by default. Only update memory files when the user explicitly asks to design or revise workflow/role memory. If the user explicitly asks for a user-level default team, edit `~/.ccb/ccb.config` instead.

## Core Workflow

1. Resolve the config authority first. CCB config precedence is built-in default < user config `~/.ccb/ccb.config` < project config `.ccb/ccb.config`. `.ccb_config/ccb.config` is legacy residue and must be treated as read-only migration evidence, not as the file to edit.
2. Read the current `.ccb/ccb.config` before proposing changes. Read memory files only when the user explicitly asks for memory/workflow guidance changes or when memory content is needed to understand an existing workflow.
3. If the user's project goal and workflow are not already clear, ask a short clarification question before designing the team.
4. After the basic workflow is clear, propose one complete config with sensible defaults and ask for confirmation or adjustments.
5. Prefer compact or hybrid config for ordinary single-window teams. Existing compact/hybrid configs stay single-window and should not be migrated to `[windows]` unless the user wants named tmux windows, multi-window sidebar layout, or per-window agent grouping.
6. When the user asks to modernize, split, or reorganize an old config, treat it as a migration task: preserve the old roster and overrides by default, propose the new target shape, then write only after confirmation.
7. For ordinary config design, migration, or layout changes, edit only `.ccb/ccb.config`.
8. If and only if the user explicitly requested workflow memory design, also update `.ccb/ccb_memory.md` and/or `.ccb/agents/<agent>/memory.md` using the memory rules below.
9. Validate the written config with the CCB config loader and verify that the loader read the intended source kind.
10. Tell the user that CCB must be restarted for config changes to take effect.

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
- whether the user wants one window or multiple named windows, and if multiple windows are desired, the rough grouping such as main/work/review/research;
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
- single-window compact layout unless you ask for named windows
- no memory files changed unless you ask for workflow memory design
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
3. Ask one concise migration question if the target shape is not already clear: how many windows and how should agents be grouped? Offer a default grouping such as `main`, `work`, and `review`.
4. If the user wants to stay single-window, keep compact/hybrid format and only adjust the compact layout or overlay fields.
5. If the user wants multi-window, named windows, or per-window sidebar layout, migrate to `version = 2` with `[windows]`.
6. In `[windows]`, remove `cmd`; a persistent `cmd` pane is a compact/hybrid feature.
7. Keep each agent in exactly one window. Use window names that match the workflow, such as `main`, `work`, `review`, `research`, or `ops`.
8. Move agent-specific extras into `[agents.<name>]` tables after the `[windows]` block.
9. Present a before/after proposal and ask for confirmation before writing.
10. Do not edit memory files during config migration unless the user explicitly asks for role or workflow memory changes.

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
- In explicit windows topology, `[windows]` defines the effective configured-agent set; same-name `[agents.<name>]` tables are overlays and may override `workspace_mode`, while stale tables for names no longer in `[windows]` are ignored.
- `cmd` is not supported inside `[windows]` topology. Use compact/hybrid config when a persistent command pane is required.
- Migration to `[windows]` is opt-in and should preserve existing agent fields unless the user asks for role/provider/workspace changes.
- `agent:provider(worktree)` maps to `workspace_mode = "git-worktree"`.
- `git-worktree` requires the project root to be a git repository; CCB must not silently fall back to copying.

## Skill Injection Requests

Use this flow when the user asks to add, inject, install, or inherit a skill for an agent, for example "inject plan-tree into agent2".

1. Read `.ccb/ccb.config` and identify the target agent provider.
2. Locate a provider-matching skill source:
   - Codex useful tool: `useful_tools/codex_skills/<skill>/`
   - Claude useful tool: `useful_tools/claude_skills/<skill>/`
   - inherited CCB skill: `inherit_skills/<provider>_skills/<skill>/`
   - user-installed source home: `${CODEX_HOME:-$HOME/.codex}/skills/<skill>` or `$HOME/.claude/skills/<skill>`
3. Explain the scope before writing. CCB config currently has `provider_profile.inherit_skills`, but no per-skill allowlist. A durable provider-home install is inherited by every same-provider agent whose `provider_profile.inherit_skills` is true.
4. Prefer durable source-home installation:
   - Codex: copy the skill into `${CODEX_HOME:-$HOME/.codex}/skills/<skill>`.
   - Claude: copy the skill into `$HOME/.claude/skills/<skill>`.
   - If the target agent has `provider_profile.inherit_skills = false`, propose enabling it in `.ccb/ccb.config`; otherwise no config change is needed for the target.
5. If the user wants only one specific agent to receive the skill, explain the current choices:
   - install globally and accept that same-provider inheriting agents also receive it;
   - disable `provider_profile.inherit_skills` on other same-provider agents, which removes all inherited skills from them and is usually not recommended;
   - make a temporary runtime copy into the already-mounted target agent home, only with explicit confirmation and with a warning that restart or projection refresh may replace it.
6. For temporary single-agent runtime injection, never follow symlinks blindly. If the target `skills` directory is a symlink, stop and explain that writing there would affect the source home. Otherwise copy only the requested skill directory and verify `SKILL.md` exists at the destination.
7. Do not edit memory files for skill injection unless the user separately asks for workflow memory design.
8. Tell the user to restart or relaunch affected CCB agents after durable installs or config changes.

## Memory Updates

Memory updates are opt-in. Do not write `.ccb/ccb_memory.md` or `.ccb/agents/<agent>/memory.md` during ordinary config design, config migration, provider changes, window layout changes, or worktree changes.

Read `references/memory-patterns.md` before writing role memory, and only do so when the user explicitly asks for workflow memory design or role memory changes.

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
- skill injection: the source and destination are provider-matching skill directories and destination `SKILL.md` exists;
- no secrets were added unless the user explicitly provided them;
- memory updates preserved existing unmarked content.

## Boundaries

- Do not bootstrap a new `.ccb/ccb.config` without user confirmation.
- Never write `.ccb_config/ccb.config`; if it exists, treat it as legacy residue only.
- Do not delete memory files for removed agents unless the user explicitly asks.
- Do not create or edit provider profile directories directly.
- Do not edit provider-state homes except for explicitly requested temporary single-agent skill injection after warning that it is not the durable config path.
- Do not change runtime state to "apply" a config; do not run `ccb`, `ccb -s`, `ccb kill`, or restart from inside the skill; tell the user to restart CCB after the skill has finished.
- Do not use `workspace_mode = "copy"` unless the user explicitly chooses copy workspace behavior.
