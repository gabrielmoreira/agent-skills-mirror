---
name: ccb-config
description: "Design, edit, or migrate CCB project teams by updating .ccb/ccb.config. Use when the user wants to configure agents, providers, roles, workspaces, windows topology, managed tool windows, sidebar behavior, model/API shortcuts, provider command templates, or runtime policy. This skill is config-only: it must not edit workflow memory, provider-state homes, installed roles, or runtime state."
---

# CCB Config

Use this skill to design, edit, or migrate CCB project configuration. The normal output is a valid `.ccb/ccb.config` or, only when explicitly requested, a user-level `~/.ccb/ccb.config`.

This skill is not a workflow-memory designer. Do not edit `.ccb/ccb_memory.md`, `.ccb/agents/<agent>/memory.md`, generated memory, provider-state homes, installed role stores, or runtime records. After finishing config work, remind the user that workflow memory can be set separately if they want persistent collaboration rules.

## Core Workflow

1. Resolve the config authority first. CCB config precedence is built-in default < user config `~/.ccb/ccb.config` < project config `.ccb/ccb.config`. `.ccb_config/ccb.config` is legacy residue and must be treated as read-only migration evidence.
2. Read the current `.ccb/ccb.config` when it exists. Do not read memory files for ordinary config work.
3. Summarize the active config source and current shape: topology type, windows, agents, tool windows, sidebar, workspace modes, and notable advanced overrides.
4. Show the configuration menu below when the user asks what can be configured, asks for broad redesign, or leaves the target vague.
5. Ask one focused clarification question only when required. Do not ask a long questionnaire.
6. Propose one complete TOML preview or one clear patch. Prefer `version = 2` `[windows]` topology unless the user explicitly wants compact/cmd.
7. Write only after confirmation or an explicit apply request.
8. Validate with the CCB config loader and verify the intended source kind.
9. Tell the user the next runtime action: usually `ccb reload --dry-run` then `ccb reload`, or restart for changes reload cannot apply.

Never run `ccb`, `ccb -s`, `ccb kill`, `ccb reload`, or restart commands as part of this skill workflow. Finish file writes and validation first, then tell the user what to run.

When this skill is used inside the CCB source checkout, keep production/work-environment commands separate from source validation. For validating current source changes, tell the user to run `ccb_test` from an external test project such as `/home/bfly/yunwei/test_ccb2`; do not suggest running source validation with bare `ccb` or from the source checkout itself.

## Language Behavior

Match the user's language for all user-facing prose. If the user writes in Chinese, present the menu, clarification question, proposal summary, warnings, and next steps in Chinese. If the user writes in English, use English. For mixed-language requests, use the dominant language of the latest user request and preserve quoted terms as written.

Do not translate CCB syntax or stable identifiers: TOML keys, table names, provider names, role ids, command names, env vars, `workspace_group`, `workspace_path`, `provider_command_template`, `startup_args`, and layout tokens stay literal. Agent names and window names should stay ASCII-safe unless the current CCB grammar explicitly allows otherwise; localized human wording belongs in `description`, `labels`, or explanatory prose.

When editing existing config, preserve the language of existing user-authored `description`, `labels`, sidebar `tips`, and comments unless the user asks to translate or rewrite them.

## Configuration Menu

Present this menu as a readable list when useful. Users can choose by section name, number, or plain language.

```text
CCB Config Options

Basic
  1. Config source             project .ccb/ccb.config or user ~/.ccb/ccb.config
  2. Topology                  version = 2 windows, or compact/cmd by request
  3. Windows                   main/work/review/research/ops grouping
  4. Agents                    names, providers, labels, descriptions
  5. Role Pack agents          agentroles.archi and other installed roles
  6. Managed tools             Neovim tool window on/off, command, label
  7. Sidebar                   mode, width, section heights, Comms, Tips

Agent Advanced
  8. Model                     per-agent model shortcut
  9. API route                 per-agent key/url shortcut
 10. Agent metadata            labels, description, role binding

Workspace Advanced
 11. Workspace mode            inplace or git-worktree
 12. Shared worktree group     per-agent workspace_group
 13. External worktree path    per-agent workspace_path
 14. Branch template           per-agent branch_template

Provider Startup Advanced
 15. Provider inheritance      provider_profile inherit_* flags
 16. Provider env              provider_profile.env or agent env
 17. Command wrapper           provider_command_template with exactly one {command}
 18. Startup args              provider startup_args after generated model args

Runtime Advanced
 19. Permission                permission
 20. Restore                   restore
 21. Queue policy              queue_policy
 22. Watch paths               watch_paths
 23. Pane split percent        layout leaf @N when supported

Output
 24. Preview TOML
 25. Apply and validate
```

Keep the first response compact. For normal users, focus on Basic. Treat Agent Advanced, Workspace Advanced, Provider Startup Advanced, and Runtime Advanced as explicit opt-in sections.

Translate the displayed menu labels and short explanations into the user's language when presenting the menu. Keep the option numbers and literal config field names unchanged.

## Advanced Grouping Rules

Use `[windows]` leaves for the visible roster and basic provider/worktree shape. Use `[agents.<name>]` overlays for per-agent advanced controls.

- Workspace Advanced is per-agent. `(worktree)` in a layout leaf only selects `workspace_mode = "git-worktree"`; write `workspace_group`, `workspace_path`, or `branch_template` under `[agents.<name>]`.
- `workspace_group` means multiple agents intentionally share one CCB-managed worktree. `workspace_path` means the user supplied an external worktree path that CCB validates but does not create, delete, copy, prune, or switch.
- Do not mix `workspace_group`, `workspace_path`, `workspace_root`, or `branch_template` for the same agent unless the reference explicitly allows the combination.
- Provider Startup Advanced is per-agent. Use `provider_command_template = "prefix {command} suffix"` for whole-command wrappers, and require exactly one `{command}`. Use `startup_args` only for provider-native trailing args that should be included inside CCB's generated command.
- Do not put model flags into `startup_args` when `model` is set. Prefer the dedicated `model`, `key`, and `url` fields for ordinary model/API routing.
- Pane split percent is layout syntax, not an agent overlay. Use `agent:provider@N` or `agent:provider(worktree)@N` only when the current CCB version supports `@percent`.

## Default Proposal

Use this default shape for new or modernized project configs unless the user asks otherwise:

```toml
version = 2
entry_window = "main"

[windows]
main = "main:codex"
work = "worker1:codex(worktree)"
review = "reviewer:claude"

[tool_windows.neovim]
command = "ccb-nvim"
label = "neovim"
```

Default rules:

- Include `[tool_windows.neovim]` by default for windows topology. Disable Neovim by omitting/removing that block; do not invent `enabled = false`.
- The built-in default used when no `.ccb/ccb.config` or `~/.ccb/ccb.config` exists already includes the managed Neovim tool window.
- Inherit provider credentials/config by default.
- Use one worker for small projects or serial workflows.
- Use 3 implementation workers when the user explicitly wants parallel execution but does not specify a count.
- Use `git-worktree` only when the project is a Git repository or the user provides a valid external worktree path.
- Keep `restore = "auto"`, `permission = "manual"`, `runtime_mode = "pane-backed"`, and `queue_policy = "serial-per-agent"` unless the user explicitly asks otherwise.
- Do not write secrets unless the user explicitly provides them and accepts they will be stored in config.

## Migration Tasks

Use this flow when converting compact/hybrid config, adding windows, reorganizing agents, adding roles, changing workspace policy, or modernizing config:

When a legacy compact or hybrid config needs structural edits, treat it as a migration task. Migration to `[windows]` is the default recommendation unless the user wants compact syntax or a persistent `cmd` pane.

1. Read the current config and identify whether it is compact, hybrid, explicit windows, or legacy rich TOML.
2. Preserve existing agent names, providers, worktree markers, models, keys, urls, descriptions, labels, permissions, restore settings, provider profiles, and role bindings unless the user asks to change them.
3. Recommend `version = 2` `[windows]` topology for structural changes.
4. Keep compact/hybrid only when the user explicitly wants a persistent `cmd` pane or asks to preserve compact format.
5. Remove `cmd` from migrated `[windows]`; `cmd` is a compact/hybrid feature.
6. Keep each configured agent in exactly one window.
7. Move agent-specific extras into `[agents.<name>]` tables after `[windows]`.
8. Include `[tool_windows.neovim]` by default unless the user asks to disable it.
9. Present before/after and ask for confirmation before writing.

Example:

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

[tool_windows.neovim]
command = "ccb-nvim"
label = "neovim"
```

## Config Knowledge

Read `references/ccb-config.md` when editing `.ccb/ccb.config` or explaining syntax.

Key points:

- Compact agent leaves must be `agent:provider` or `agent:provider(worktree)`.
- When supported by the current CCB version, a layout leaf may add `@N` as a pane split hint, for example `main:codex@60`.
- `cmd` is a compact/hybrid layout keyword, not an agent.
- `;` creates horizontal columns; `,` creates vertical rows; parentheses group layout expressions.
- Explicit windows topology uses `version = 2`, `[windows]`, optional `[tool_windows]`, optional `[ui.sidebar]`, and optional `[agents.<name>]` overlays.
- `[windows]` defines the effective configured-agent set. Same-name `[agents.<name>]` tables are overlays; stale tables for names no longer in `[windows]` are ignored.
- `agent:provider(worktree)` maps to `workspace_mode = "git-worktree"`.
- `workspace_group` shares one CCB-managed worktree among agents.
- `workspace_path` points to an external worktree that CCB validates but does not create, delete, copy, prune, or switch.
- `model` compiles to provider model startup args and must not be combined with model flags in `startup_args`.
- `key` and `url` are agent-local API shortcuts for supported providers.
- `provider_command_template` must contain exactly one `{command}` and wraps CCB's generated provider command segment without replacing env/home/resume logic.

## Role Pack Agents

Use canonical Role Pack ids in new config. For Archi, write `agentroles.archi`, not `ccb.archi`.

Preferred shorthand:

```toml
[windows]
main = "main:codex, agentroles.archi:codex"
```

Equivalent explicit binding:

```toml
[windows]
main = "main:codex, archi:codex"

[agents.archi]
role = "agentroles.archi"
provider = "codex"
```

Rules:

- Keep the project-local ask target natural, usually `archi`.
- If validation reports the role is missing, tell the user to run `ccb roles install agentroles.archi`.
- To diagnose role package health, tell the user to run `ccb roles doctor agentroles.archi`.
- If the user wants the CLI shortcut, use `ccb roles add agentroles.archi:codex`.
- After the role is configured, talk to the local agent with `ccb ask archi "..."`.
- Do not copy role memory or skills into `.ccb`; CCB projects role assets from the installed role store.
- Do not write role store paths into `.ccb/ccb.config`.

## Skill Inheritance

Config supports provider-level inheritance flags such as:

```toml
[agents.worker1.provider_profile]
inherit_skills = true
inherit_commands = true
inherit_memory = true
```

This is only a config switch for provider source-home inheritance. Do not install skills, copy skills into provider homes, or perform one-agent temporary skill injection in this skill.

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

After editing `~/.ccb/ccb.config`, validate from a temporary directory without a project config and require `source_kind == "user_config"`.

Also check:

- agent names are valid and not reserved;
- compact/hybrid config has each configured agent exactly once and `cmd` first when enabled;
- windows topology has each configured agent in exactly one `[windows]` layout and no `cmd` leaf;
- worktree markers are represented in the compact/window layout or matching overlay fields;
- validation reports the intended source kind and path;
- no secrets were added unless explicitly requested;
- no memory, runtime, provider-state, or installed-role files were edited.

## Boundaries

- Do not bootstrap a new `.ccb/ccb.config` without user confirmation.
- Never write `.ccb_config/ccb.config`.
- Do not edit `.ccb/ccb_memory.md` or `.ccb/agents/<agent>/memory.md`.
- Do not create or edit provider profile directories directly.
- Do not edit provider-state homes, installed role stores, generated memory, `.ccb/ccbd/`, or runtime state.
- Do not use `workspace_mode = "copy"` unless the user explicitly chooses copy workspace behavior.
- End by reminding the user that workflow memory/collaboration rules are separate from config and can be set separately if desired.
