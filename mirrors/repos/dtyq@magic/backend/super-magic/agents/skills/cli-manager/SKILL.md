---
name: cli-manager
description: Manage persistence for user-installed third-party CLI tools in the Super Magic sandbox. Use when the user wants to install, configure, adopt, restore, inspect, or remove a CLI, or when an external skill, webpage, or installer asks to run CLI install commands such as curl|sh, npm install -g, pipx install, uv tool install, go install, cargo install, or brew install. Do not persist runtime-provided CLIs.
---

# CLI Manager

Use this skill when the user wants to install a user-managed third-party CLI, or when a user-installed CLI should remain available across future sandbox sessions.

This skill is for orchestration only. Do not handle installed artifacts yourself, and do not guess how the tool implements persistence. All persistence, restore, conflict detection, and cleanup actions must go through the Code Mode tools.

## Principles

1. Separate runtime-provided CLIs from user-managed CLIs before discussing persistence.
2. `lark-cli`, `dws`, and `teamshare-cli` are provided and updated by the Super Magic runtime. Never install, adopt, or create new persistence records for them with cli-manager.
3. If the user asks to install one of those runtime-provided CLIs and the command is available, tell the user it is already installed and continue with its platform skill or authentication flow. Do not ask for persistence confirmation.
4. If a runtime-provided CLI is unavailable, report it as a runtime environment problem. Do not repair it by installing a user-managed copy.
5. `cli_manager_list` lists only user-managed persisted CLIs. An empty result says nothing about runtime-provided CLIs.
6. If a runtime-provided CLI already has a legacy user persistence record, explain that the record is redundant. Remove only that legacy record after explicit user confirmation.
7. Before running any third-party CLI install command, decide whether user persistence is needed.
8. Before persisting or removing a user-managed CLI, get explicit user confirmation.
9. For script-based installers such as `curl ... | sh`, `wget ... | bash`, or `sh install.sh`, read the full installer script first and continue only if there is no obvious high-risk behavior.
10. Store secret values such as API keys, tokens, and licenses with `env-manager`. This skill only records environment variable names.
11. If a tool fails, stop the current install or remove flow and follow the next steps in `result.content`.
12. Do not read or rely on `extra_info`, `data`, or other internal fields unless a later tool document explicitly requires it.
13. Use only the parameters shown in this skill. Never pass `resolution`, `resolution_options`, or other guessed internal parameters.
14. Do not run the actual install command with `shell_exec`. `cli_manager_apply` is responsible for executing the installer after confirmation.

## Install Flow

1. Check whether the requested command is runtime-provided. If it is `lark-cli`, `dws`, or `teamshare-cli`, follow the runtime-provided short circuit above and stop this install flow.
2. Identify the CLI name, command names, install command, relevant config directories, and required environment variable names.
3. If the install path depends on a remote or local installer script, read the full script and check for obvious risk before continuing.
4. Tell the user that a normal user-managed install can be lost when the sandbox is destroyed, then ask whether they want to persist the CLI.
5. After the user confirms, call `cli_manager_apply`.
6. If the install docs require an API key first, load `env-manager` to check or save the required environment variable before continuing.
7. After install completes, verify and respond based on `result.content`.
8. If `cli_manager_apply` fails, do not run the CLI with `shell_exec` to turn the flow into a success. Follow the next steps in `result.content` or report that persistence did not complete.

Install a new CLI:

```python
run_sdk_snippet(python_code="""
from sdk.tool import tool

result = tool.call("cli_manager_apply", {
    "name": "example-cli",
    "mode": "install",
    "install_command": "npm install -g example-cli",
    "commands": ["example-cli"],
    "config_dirs": ["~/.example-cli"],
    "env_keys": ["EXAMPLE_API_KEY"],
    "confirmed": True,
})
if not result.ok:
    print(result.content)
    raise SystemExit(1)
print(result.content)
""")
```

Adopt an already installed CLI:

```python
run_sdk_snippet(python_code="""
from sdk.tool import tool

result = tool.call("cli_manager_apply", {
    "name": "example-cli",
    "mode": "adopt",
    "commands": ["example-cli"],
    "config_dirs": ["~/.example-cli"],
    "env_keys": [],
    "confirmed": True,
})
if not result.ok:
    print(result.content)
    raise SystemExit(1)
print(result.content)
""")
```

## Inspect Flow

When the user wants to inspect persisted CLIs, check whether restore succeeded, or diagnose an unavailable command, call `cli_manager_list`.

```python
run_sdk_snippet(python_code="""
from sdk.tool import tool

result = tool.call("cli_manager_list", {"validate": True})
if not result.ok:
    print(result.content)
    raise SystemExit(1)
print(result.content)
""")
```

## Remove Flow

Only remove a persisted CLI after explicit user confirmation. By default, remove only the CLI persistence. Set `remove_state=True` only when the user explicitly asks to also delete that CLI's saved state.

```python
run_sdk_snippet(python_code="""
from sdk.tool import tool

result = tool.call("cli_manager_remove", {
    "name": "example-cli",
    "remove_state": False,
    "confirmed": True,
})
if not result.ok:
    print(result.content)
    raise SystemExit(1)
print(result.content)
""")
```

## Conflict Handling

When a conflict occurs, do not overwrite, delete, or rename anything yourself. Read `result.content`, show the conflict to the user, and ask them to choose one of the next steps.

If the user chooses to adopt an existing command, call `cli_manager_apply` again with `mode="adopt"` and the same command names.

If the user chooses to replace an existing persisted CLI, call `cli_manager_remove` first after confirmation, then retry `cli_manager_apply`.

If the user chooses to replace a command that is outside cli-manager, ask before removing anything and retry only after the conflict is gone.

If the user chooses a different command name, make sure it is a real command name or an installer-supported alias before retrying.

If the user cancels, stop the flow and report that no persistence change was made.

Do not pass `resolution`, `resolution_options`, `preferred_strategy`, `command_paths`, or `extra_bin_dirs`. They are not orchestration inputs.

## Final Response

After success, briefly tell the user:

- the CLI name and command names
- whether it has been persisted
- whether any environment variables are still missing
- how they can run or verify it next
