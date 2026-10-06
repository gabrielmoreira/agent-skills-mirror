---
name: pyats-parallel-ops
description: "Fleet-wide parallel device operations: concurrent health checks, config audits, routing snapshots, severity-sorted reporting, and failure-isolated multi-device automation. Use when checking multiple devices or collecting fleet baselines through pyATS MCP."
license: Apache-2.0
user-invocable: true
metadata:
  { "openclaw": { "requires": { "env": ["PYATS_TESTBED_PATH"] } } }
---

# Parallel Fleet Operations

## Runtime and discovery

Use the modern pyATS MCP Streamable HTTP server. For stateless HTTP set
`PYATS_MCP_TRANSPORT_MODE=stateless` on the server. Discover its actual tool
schemas before calling tools; an older installed clone may lack native pCalls.
The modern server does not support direct STDIO. NetClaw provides
`scripts/pyats-stdio.py` as a compatibility bridge to its stateless HTTP runtime;
set `PYATS_MCP_SCRIPT` to that bridge (see `docs/PYATS-HTTP-MIGRATION.md`). Merely listing
several shell commands does not execute a pyATS pCall.

Start every session with `pyats_list_devices` using `{}`. Use returned device
names, group by role or site, and confirm the requested scope. Never invent
device names or infer current operational state from a saved testbed.

Stateless HTTP describes protocol session handling; it does not mean the server
has no caches, operation history, or stored snapshots. Do not depend on snapshots
surviving a process restart. Keep configuration initialization disabled for
read-only checks (`init_config_commands: []` in testbed connection arguments).

## Native parallel execution

For process-isolated read-only fan-out, call `pyats_pcall_show_command`:

```json
{"device_names":["R1","R2","SW1"],"command":"show version"}
```

This uses `pyats.async_.pcall`, one child process per device. The response contains
per-device results, a summary, and a concurrency field. Verify each result:
an outer `status: completed` does not mean every device succeeded.

`pyats_run_show_command_multi` provides thread-based fan-out with lower overhead.
Use it for routine collection when shared-process behavior is acceptable. Choose
native pCall when process isolation is required or explicitly requested. Separate
agent calls running concurrently are a third mechanism, not native pCall.

## Fleet health workflow

Run one fleet call per command, collecting the results of each wave before the
next. Avoid competing connections and commands to the same device.

1. `show version` — platform, image, uptime.
2. `show processes cpu sorted` — CPU and top consumers.
3. `show ip interface brief` — interface and protocol state.
4. Role-appropriate routing checks, such as `show ip ospf neighbor` or
   `show ip bgp summary`, only on devices where those protocols apply.
5. Additional memory, NTP, CDP/LLDP, or log checks appropriate to the platform.

Use the discovered schema and supply `device_names` and `command` as above.
Show-command tools require a supported show command; do not use shell pipelines,
configuration commands, or destructive operations as shortcuts.

Keep raw configurations, topology, testbed credentials, and device output local.
Prefer environment references for testbed secrets. Never include credentials in
reports, tracked fixtures, or external communications.

## Failure handling and reporting

Produce a result for every requested device. A connection failure, timeout,
command failure, or parse failure must be visible without discarding successful
results. If the server returns an aggregate error, reconcile missing device
results explicitly. Retry only appropriate read-only operations with a bounded
budget; do not classify a device as healthy because a tool returned HTTP 200.

Raw-output fallback is evidence of command execution, not successful structured
parsing. Label it accordingly. Investigate CPU above 90%, unexpected non-FULL
OSPF neighbors, and BGP IDLE/ACTIVE peers using additional read-only checks.
Do not change configuration to repair a health finding without the change
management workflow.

Report severity first, then device, evidence, impact, and recommended action.
Include requested/succeeded/failed counts, commands, elapsed time, and any
unverified checks. Separate unreachable devices from confirmed unhealthy ones;
a timeout alone does not establish production impact or incident severity.

## Configuration and baselines

Follow `pyats-config-mgmt` and the repository change-management rules. Capture a
baseline, check affected CIs, obtain the required approved ServiceNow change,
then apply and verify. Creating external tickets requires the applicable user
authorization. Never treat read-only fleet authorization as configuration consent.

The modern server exposes `pyats_pcall_configure_devices` and
`pyats_configure_devices_multi`; discover their current schemas and honor the
same gates for either. Parallel execution does not make changes atomic. Record
partial failures, verify each device, and do not close a failed change.

## Scale and audit

For a small lab, use one bounded device group per wave. For larger fleets, group
by role/site and start with modest batches (for example, 5–10 devices), adjusting
to measured server and device capacity. Sampling must be reported as sampling;
it does not certify unsampled devices.

Record fleet scope, baselines, findings, changes if authorized, and verification
in GAIT. Finish with one fleet summary and `gait_log`. Related skills:
`pyats-health-check`, `pyats-security`, `pyats-topology`, `pyats-config-mgmt`, and
`pyats-dynamic-test`.

## MCP Tasks

For eligible tools, a client declaring the current Tasks extension may receive a task handle. Retain it and poll for the terminal result; do not resubmit pending work. Ordinary clients continue receiving foreground results. A handle is not execution success or approval: preserve required baseline/change-control checks before invocation and verify the completed result afterward. Cancellation cannot undo commands already sent. Investigate unknown outcomes before retrying. pyATS retains completed results in SQLite and lets started work finish; other FastMCP tools default to ephemeral state and cooperative cancellation. See `docs/MCP-TASKS.md`.
