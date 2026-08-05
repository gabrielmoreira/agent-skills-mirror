---
name: search-agents
description: Use when a task should be delegated to a digital employee (Crew agent) but the target is not yet decided or not yet installed locally — discover available employees and prepare the chosen one before dispatching. Pair with the subagents skill, which performs the actual call_subagent dispatch.
---

# Search & Prepare Agents

This skill finds the right agent for a task and makes it dispatchable. It does NOT run the task itself — once an agent is prepared, hand off to `call_subagent` (from the `subagents` skill).

Two responsibilities:

1. Discover available digital employees (Crew agents) with `agent_list`.
2. Prepare a chosen target with `prepare_agent` so `call_subagent` can load it.

Built-in agents (`magic`, `explore`, `shell`, `search`) need no discovery and no download — call them directly with `call_subagent`. Use this skill when you need a Crew digital employee, or when you are unsure which employee fits.

## Workflow

```
1. agent_list            -> see available employees (code, name, description)
2. prepare_agent(code)   -> download + compile the employee into a local .agent
3. call_subagent(name)   -> dispatch the task (see the subagents skill)
```

Skip step 1 if the user already named a specific employee code. Skip steps 1–2 entirely for built-in agent types.

## Tool: agent_list

Lists Crew employees available to the current user.

```python
from sdk.tool import tool

result = tool.call("agent_list", {
    "name_filter": str,  # optional; one or more keywords in the user's language, space/comma separated
    "limit": int,        # optional; default 30, max 100
})
print(result.content)
```

- `name_filter` is matched server-side against employee name and description; any keyword hit returns the employee. If nothing matches, the full list is returned so you can still choose.
- Each entry exposes `code` (the employee identifier, e.g. `SMA-xxxx`), `name`, and `description`. Choose by name and description.

## Tool: prepare_agent

Makes a chosen agent dispatchable by `call_subagent`.

```python
from sdk.tool import tool

result = tool.call("prepare_agent", {
    "agent_code": str,  # required; a Crew code (SMA-...) from agent_list, or a built-in name/alias
})
print(result.content)
```

- For a Crew code (`SMA-...`): downloads and compiles the employee into a local `.agent`. The result's `data["agent_name"]` is the local name to dispatch.
- For a built-in name/alias: normalizes it to the canonical agent name (e.g. `ppt` -> `slider`).
- Always read `result.content` for the exact `agent_name` to pass to `call_subagent`.

## Dispatching after preparation

Once `prepare_agent` reports an agent is ready, dispatch it with `call_subagent` using the returned `agent_name`. See the `subagents` skill for `call_subagent` and `wait_for_subagents` usage, prompt construction, parallel dispatch, and output-target rules.

```python
from sdk.tool import tool

prepared = tool.call("prepare_agent", {"agent_code": "SMA-xxxx"})
agent_name = prepared.data["agent_name"]

tool.call("call_subagent", {
    "agent_name": agent_name,
    "agent_id": "market-research-phase1",
    "prompt": "<self-contained task with context, expected output, and success criteria>",
    "background": False,
})
```

## Notes

- Sub-agents cannot delegate further: only the root agent may discover, prepare, and dispatch.
- `prepare_agent` is idempotent — re-preparing an already-installed employee is cheap and safe.
- If `agent_list` or `prepare_agent` reports delegation is not enabled, the current agent is missing the `subagents` skill; it must be enabled before delegating.
