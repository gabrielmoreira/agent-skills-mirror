---
name: env-manager
description: Use when the user provides API keys, tokens, or other configuration values that should persist across sessions, or when the user asks to query, list, or delete saved environment variables. Manages personal env by default and workspace env only when explicitly requested.
---

# Environment Variable Manager

Use this skill by calling `set_env`, `get_env`, `unset_env`, and `list_env` through `sdk.tool.call(...)` inside `run_sdk_snippet`.

By default, save and delete personal environment variables stored in `~/.magic/super-magic.env` for reuse across workspaces.
Pass `"scope": "workspace"` only when the user explicitly asks to save or delete values for the current workspace/project.

The runtime effective environment merges workspace env and personal env. Personal env has the highest priority and overrides workspace values with the same key.
Tool display and results never echo plaintext values.

## Get One Env

When you only need to check whether one key is configured, prefer `get_env`. `get_env` queries the final effective env by default (`scope=all`). Do not call `list_env` just to inspect one key, because that exposes unrelated environment variable names and masked values to the model context.

```python
run_sdk_snippet(python_code="""
from sdk.tool import tool

result = tool.call("get_env", {
    "key": "KEY_NAME",
})
if not result.ok:
    raise SystemExit(result.content)
print(result.content)
""")
```

Only pass `"scope": "personal"` or `"scope": "workspace"` when you need to check whether a key exists in a specific storage scope.

```python
run_sdk_snippet(python_code="""
from sdk.tool import tool

result = tool.call("get_env", {
    "key": "KEY_NAME",
    "scope": "workspace",
})
if not result.ok:
    raise SystemExit(result.content)
print(result.content)
""")
```

## Set Personal Env

```python
run_sdk_snippet(python_code="""
from sdk.tool import tool

result = tool.call("set_env", {
    "key": "KEY_NAME",
    "value": "value",
})
if not result.ok:
    raise SystemExit(result.content)
print(result.content)
""")
```

## Set Workspace Env

```python
run_sdk_snippet(python_code="""
from sdk.tool import tool

result = tool.call("set_env", {
    "key": "KEY_NAME",
    "value": "value",
    "scope": "workspace",
})
if not result.ok:
    raise SystemExit(result.content)
print(result.content)
""")
```

## List Personal Env

```python
run_sdk_snippet(python_code="""
from sdk.tool import tool

result = tool.call("list_env", {})
if not result.ok:
    raise SystemExit(result.content)
print(result.content)
""")
```

## List Workspace Env

```python
run_sdk_snippet(python_code="""
from sdk.tool import tool

result = tool.call("list_env", {
    "scope": "workspace",
})
if not result.ok:
    raise SystemExit(result.content)
print(result.content)
""")
```

## List Effective Env

`"scope": "all"` means the final effective merge of workspace and personal env. Personal env overrides workspace env with the same key.

```python
run_sdk_snippet(python_code="""
from sdk.tool import tool

result = tool.call("list_env", {
    "scope": "all",
})
if not result.ok:
    raise SystemExit(result.content)
print(result.content)
""")
```

## Unset Personal Env

```python
run_sdk_snippet(python_code="""
from sdk.tool import tool

result = tool.call("unset_env", {
    "key": "KEY_NAME",
})
if not result.ok:
    raise SystemExit(result.content)
print(result.content)
""")
```

## Unset Workspace Env

```python
run_sdk_snippet(python_code="""
from sdk.tool import tool

result = tool.call("unset_env", {
    "key": "KEY_NAME",
    "scope": "workspace",
})
if not result.ok:
    raise SystemExit(result.content)
print(result.content)
""")
```
