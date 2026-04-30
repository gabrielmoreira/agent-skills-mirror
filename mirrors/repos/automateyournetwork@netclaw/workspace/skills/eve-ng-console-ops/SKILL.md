---
name: eve-ng-console-ops
description: Execute commands on running EVE-NG nodes through the console for IOS, Junos, VPCS, EOS, and NX-OS.
user-invocable: true
metadata:
  openclaw:
    requires:
      bins: ["python3"]
      env: ["EVE_URL", "EVE_USER", "EVE_PASSWORD"]
---

# EVE-NG Console Operations

Use this skill when the lab is already running and you need live CLI access.

## When to Use

- Run show commands on active devices
- Push configuration interactively
- Verify routing adjacencies after topology changes
- Test reachability with `ping` or `traceroute`
- Confirm console readiness after node boot

## Console Rules

- Run `eve_discover_node` first when readiness is uncertain.
- Treat API `running` state as separate from console readiness.
- Keep command batches focused; long transcripts consume tokens fast.
- Use config mode only when the task truly needs it.

## MCP Server

- **Command**: `python3 -u mcp-servers/eve-ng-mcp-server/eve_ng_mcp_server.py`
- **Requires**: `EVE_URL`, `EVE_USER`, `EVE_PASSWORD`
- **Optional**: `EVE_CONSOLE_HOST` when the MCP server runs off-box

## Available Tools

| Tool | Parameters | Purpose |
|---|---|---|
| `eve_discover_node` | `lab_path, node` | Resolve console host, port, and runtime status |
| `eve_exec_ios` | `lab_path, node, commands, config_mode?, save?, command_timeout?, wait?` | IOS / IOL / IOS-XE console |
| `eve_exec_junos` | `lab_path, node, commands, command_timeout?, wait?` | Junos console |
| `eve_exec_vpcs` | `lab_path, node, commands, command_timeout?, dhcp_timeout?, prompt_timeout?` | VPCS console |
| `eve_exec_eos` | `lab_path, node, commands, config_mode?, save?, command_timeout?, wait?` | Arista EOS console |
| `eve_exec_nxos` | `lab_path, node, commands, config_mode?, save?, command_timeout?, wait?` | Cisco NX-OS console |

## Workflow Examples

```text
"Is R1 ready for CLI access?"                            → eve_discover_node /Labs/bgp-demo.unl R1
"Run show ip route on R1"                                → eve_exec_ios /Labs/bgp-demo.unl R1 ["show ip route"]
"Show bgp summary on vMX1"                               → eve_exec_junos /Labs/wan-demo.unl vMX1 ["show bgp summary"]
"Run DHCP then ping from PC1"                            → eve_exec_vpcs /Labs/access-demo.unl PC1 ["ip dhcp", "ping 10.0.0.1"]
"Create VLAN 10 on SW1 and save"                         → eve_exec_nxos config_mode=true save=true
```

## Output Model

Exec tools return a `transcript` array with one entry per command. Prefer targeted command sets instead of large diagnostic dumps.

## Timeout Tuning

- Raise `command_timeout` for slow boots or large outputs.
- Raise `wait` if the guest CLI is sluggish.
- Use the smallest values that still produce clean prompts.

## Integration with Other Skills

- **eve-ng-node-operations**: boot or stop nodes
- **eve-lab-topology-build**: verify links after rewiring
- **eve-ng-config-ops**: compare startup vs running state

## Error Handling

| Error Code | Meaning | Resolution |
|---|---|---|
| `EVE_CONSOLE_TIMEOUT` | Console not reachable | Check node state and wait for boot |
| `EVE_NOT_FOUND` | Node name unresolved | Run `eve_list_nodes` |
| `EVE_CONSOLE_AUTH` | Login failed | Verify node credentials |

## Notes

- Junos output automatically suppresses pagination.
- `save=true` writes config using the platform-appropriate save command.
- Console transcripts can get large quickly; ask for only what you need.
