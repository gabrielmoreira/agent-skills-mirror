---
name: sandbox-manager
description: Inspect, upgrade, or restart the sandbox this Agent is running in. Use when the user asks about this Agent's sandbox status or Agent image version, or explicitly asks to upgrade or restart its current environment.
---

# Sandbox Manager

This skill manages the execution environment hosting the current Agent. “Current sandbox” means the environment running this Agent process, not an arbitrary sandbox selected by the user.

These are Code Mode tools. Execute every example through `run_sdk_snippet` with `sdk.tool.call(...)`; do not invent or pass a sandbox ID.

## Read the result correctly

`result.content` is the model-facing summary. `result.data` is the structured payload for programmatic decisions. A `run_sdk_snippet` call only exposes its standard output to the outer Agent, so print both values when inspecting a result.

Use this error pattern:

```python
if not result.ok:
    print(result.content)
    raise SystemExit(1)
```

## Inspect the current sandbox

Use `get_sandbox_info` for the current sandbox ID, runtime status, current Agent image version, latest available version, and update flag.

```python
run_sdk_snippet(python_code="""
from sdk.tool import tool

result = tool.call("get_sandbox_info", {})
if not result.ok:
    print(result.content)
    raise SystemExit(1)

print(result.content)
print(result.data)

data = result.data
if data["needs_update"]:
    print("Latest image:", data["latest_version"])
""")
```

Typical `result.content`:

```text
Current sandbox information:
- Sandbox ID: sandbox_example
- Status: Running
- Current Agent image version: v1
- Latest Agent image version: v2
- Update needed: yes
```

Typical `result.data`:

```json
{
  "sandbox_id": "sandbox_example",
  "status": "Running",
  "current_version": "v1",
  "latest_version": "v2",
  "needs_update": true
}
```

`status` is one of `Pending`, `Running`, `Exited`, `Unknown`, or `NotFound`. Version strings can be empty when the service cannot determine them.

## Upgrade the current sandbox

Call `upgrade_sandbox` only after the user explicitly asks to upgrade this sandbox to the latest Agent image. It does nothing when the image is already current.

```python
run_sdk_snippet(python_code="""
from sdk.tool import tool

result = tool.call("upgrade_sandbox", {})
if not result.ok:
    print(result.content)
    raise SystemExit(1)

print(result.content)
print(result.data)

data = result.data
if data["operation"] == "already_current":
    print("No rebuild is needed")
elif data["operation"] == "upgrade_scheduled":
    print("Scheduled after", data["delay_seconds"], "seconds")
""")
```

When an update is needed, the tool schedules the existing rebuild API and returns before rebuilding:

```text
The current sandbox upgrade has been scheduled. The sandbox is scheduled to be rebuilt in 10 seconds. Reply to the user now and do not call more tools. This confirms scheduling, not completion; after the sandbox is available again, use get_sandbox_info to verify the new image version.
```

Typical scheduled `result.data`:

```json
{
  "sandbox_id": "sandbox_example",
  "operation": "upgrade_scheduled",
  "current_version": "v1",
  "latest_version": "v2",
  "needs_update": true,
  "delay_seconds": 10
}
```

If the image is already current, the result is:

```json
{
  "sandbox_id": "sandbox_example",
  "operation": "already_current",
  "current_version": "v2",
  "latest_version": "v2",
  "needs_update": false,
  "delay_seconds": 0
}
```

`upgrade_scheduled` means only that a delayed rebuild request was created in the current Agent process. It does not mean the new image is running. Send the user a short final response immediately and do not call another tool in the same run. After the Agent is available again, call `get_sandbox_info` to verify the actual image version.

## Restart the current sandbox

Call `restart_sandbox` only after the user explicitly asks to restart this sandbox, regardless of its image version.

```python
run_sdk_snippet(python_code="""
from sdk.tool import tool

result = tool.call("restart_sandbox", {})
if not result.ok:
    print(result.content)
    raise SystemExit(1)

print(result.content)
print(result.data)

data = result.data
if data["operation"] == "restart_scheduled":
    print("Restart accepted; delay:", data["delay_seconds"], "seconds")
""")
```

Typical `result.content`:

```text
The unconditional restart of the current sandbox has been scheduled. The sandbox is scheduled to be rebuilt in 10 seconds. Reply to the user now and do not call more tools. This confirms scheduling, not completion; after the sandbox is available again, use get_sandbox_info to verify its status.
```

Typical `result.data`:

```json
{
  "sandbox_id": "sandbox_example",
  "operation": "restart_scheduled",
  "delay_seconds": 10
}
```

For a scheduled restart, `sandbox_id` is the ID of the sandbox being replaced. It is not a promise that the rebuilt sandbox will have the same ID. The delayed request is held by the current Agent process, so a process crash or a new run that cancels the pending action can prevent it from executing. Send the user a short final response immediately and do not call another tool in the same run. After recovery, use `get_sandbox_info` to inspect the new sandbox.

## Safety and persistence

- Never upgrade or restart merely because `needs_update` is true; both operations require explicit user intent.
- Save required work in `.workspace` before a rebuild. Files there persist across sandbox rebuilds; processes, temporary VM state, and files outside `.workspace` do not.
- The tool waits 10 seconds after scheduling before it sends the rebuild request. This gives the Agent time to send its final response, but the delay is intentionally in-process: a process crash or deployment can lose the pending request.
- A new user message or interruption before the rebuild request completes cancels the pending task.
- Do not automatically retry a failed or interrupted upgrade/restart. Inspect the returned error, and after recovery use `get_sandbox_info` before deciding what to do next.
