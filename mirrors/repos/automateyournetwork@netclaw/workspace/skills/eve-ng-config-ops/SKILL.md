---
name: eve-ng-config-ops
description: Manage EVE-NG startup configs — read, write, wipe, and bulk-export node configurations.
user-invocable: true
metadata:
  openclaw:
    requires:
      bins: ["python3"]
      env: ["EVE_URL", "EVE_USER", "EVE_PASSWORD"]
---

# EVE-NG Config Operations

Use this skill for startup config handling stored in the lab file.

## When to Use

- Back up startup configs before a change
- Preload startup configs before first boot
- Clear startup config without a full node wipe
- Export all configs from a lab in one call

## Config vs Wipe

| Operation | Effect | Node State |
|---|---|---|
| `eve_set_node_config` | Write startup config | Stopped |
| `eve_wipe_node_config` | Clear startup config only | Stopped |
| `eve_wipe_node` | Clear NVRAM and startup state | Stopped |

## MCP Server

- **Command**: `python3 -u mcp-servers/eve-ng-mcp-server/eve_ng_mcp_server.py`
- **Requires**: `EVE_URL`, `EVE_USER`, `EVE_PASSWORD`

## Available Tools

| Tool | Parameters | Purpose |
|---|---|---|
| `eve_get_node_config` | `lab_path, node` | Read one startup config |
| `eve_set_node_config` | `lab_path, node, config` | Write one startup config |
| `eve_get_all_configs` | `lab_path` | Export all startup configs |
| `eve_wipe_node_config` | `lab_path, node` | Clear one startup config |

## Workflow Examples

```text
"Export all configs from /Labs/bgp-demo.unl"           → eve_get_all_configs /Labs/bgp-demo.unl
"Show the stored config for R1"                        → eve_get_node_config /Labs/bgp-demo.unl R1
"Load a startup config onto R2"                        → eve_stop_node → eve_set_node_config → eve_start_node
"Clear only the startup config for R3"                 → eve_stop_node → eve_wipe_node_config → eve_start_node
```

## Provisioning Flow

1. Create the lab with **eve-ng-lab-management**.
2. Add nodes with **eve-ng-node-operations**.
3. Wire links with **eve-lab-topology-build**.
4. Load startup configs while nodes are stopped.
5. Start the lab.
6. Verify with **eve-ng-console-ops**.

## Integration with Other Skills

- **eve-ng-node-operations**: stop before write, start after write
- **eve-ng-console-ops**: verify applied config on boot
- **eve-lab-topology-design**: map design intent to startup configs

## Error Handling

| Error Code | Meaning | Resolution |
|---|---|---|
| `EVE_NOT_FOUND` | Node not found | Run `eve_list_nodes` |
| `EVE_VALIDATION` | Config rejected by API | Check formatting and line endings |
| `EVE_AUTH_FAILED` | Session failed | Retry after auth check |

## Notes

- Startup configs are stored in the `.unl` data model.
- `eve_set_node_config` does not validate vendor syntax.
- `eve_get_all_configs` is the most efficient backup path for multi-node labs.
