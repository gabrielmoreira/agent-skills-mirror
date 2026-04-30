---
name: eve-ng-node-operations
description: Manage EVE-NG nodes — list, inspect, create, delete, start, stop, and wipe nodes or full labs.
user-invocable: true
metadata:
  openclaw:
    requires:
      bins: ["python3"]
      env: ["EVE_URL", "EVE_USER", "EVE_PASSWORD"]
---

# EVE-NG Node Operations

Use this skill for node lifecycle work inside an existing lab.

## When to Use

- List nodes and runtime state
- Read node details such as image, CPU, RAM, and console port
- Add or remove nodes
- Start or stop one node or a full lab
- Wipe a node back to factory state

## Operational Rules

- Confirm the target lab first with **eve-ng-lab-management**.
- After `eve_start_node`, verify console readiness with **eve-ng-console-ops** before sending config.
- Stop nodes before deleting or wiping them.
- For bulk changes, prefer a full lab stop/start window over piecemeal churn.

## MCP Server

- **Command**: `python3 -u mcp-servers/eve-ng-mcp-server/eve_ng_mcp_server.py`
- **Requires**: `EVE_URL`, `EVE_USER`, `EVE_PASSWORD`

## Available Tools

| Tool | Parameters | Purpose |
|---|---|---|
| `eve_list_nodes` | `lab_path` | List nodes with status, image, and console |
| `eve_get_node` | `lab_path, node` | Get full details for one node |
| `eve_create_node` | `lab_path, name, node_type, template, image?, left?, top?, ram?, ethernet?, serial?, console?, cpu?, icon?` | Add a node |
| `eve_delete_node` | `lab_path, node` | Delete a node |
| `eve_start_node` | `lab_path, node` | Start one node |
| `eve_stop_node` | `lab_path, node` | Stop one node |
| `eve_start_lab` | `lab_path` | Start all nodes in a lab |
| `eve_stop_lab` | `lab_path` | Stop all nodes in a lab |
| `eve_wipe_node` | `lab_path, node` | Clear NVRAM and startup state |

Nodes can be referenced by **name** or **numeric ID**.

## Workflow Examples

```text
"List nodes in /Labs/bgp-demo.unl"          → eve_list_nodes /Labs/bgp-demo.unl
"Start R1 in /Labs/bgp-demo.unl"            → eve_start_node /Labs/bgp-demo.unl R1
"Stop all nodes in /Labs/wan-demo.unl"      → eve_stop_lab /Labs/wan-demo.unl
"Add a vIOS router named R3"                → eve_create_node /Labs/bgp-demo.unl R3 qemu vios
"Delete PC2 from /Labs/access-demo.unl"     → eve_delete_node /Labs/access-demo.unl PC2
"Wipe R2 back to defaults"                  → eve_stop_node → eve_wipe_node
```

## Verification Behavior

Start and stop tools poll EVE-NG after the action. Treat API state as necessary but not sufficient for device readiness.

Use **eve-ng-console-ops** for final confirmation when the next step depends on CLI availability.

## Integration with Other Skills

- **eve-ng-lab-management**: lab inventory and metadata
- **eve-lab-topology-build**: connect interfaces after node creation
- **eve-ng-console-ops**: verify boot readiness and run commands
- **eve-ng-config-ops**: preload or clear startup configs

## Error Handling

| Error Code | Meaning | Resolution |
|---|---|---|
| `EVE_NOT_FOUND` | Node not found | Run `eve_list_nodes` |
| `EVE_CONFLICT` | Duplicate node name | Use a unique name |
| `EVE_VALIDATION` | Invalid node type or template | Check `eve_list_node_types` and installed images |
| `EVE_IMAGE_MISSING` | Image not installed | Run `eve_list_images` |
| `EVE_AUTH_FAILED` | Session failed | Retry after auth check |

## Notes

- Use image names exactly as installed on the EVE host.
- Canvas coordinates are cosmetic.
- Wipe is destructive for node state; use **eve-ng-config-ops** for config-only resets.
