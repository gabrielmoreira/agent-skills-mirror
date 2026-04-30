---
name: eve-lab-topology-build
description: Build and wire EVE-NG topologies — inspect links, create networks, and connect node interfaces.
user-invocable: true
metadata:
  openclaw:
    requires:
      bins: ["python3"]
      env: ["EVE_URL", "EVE_USER", "EVE_PASSWORD"]
---

# EVE Lab Topology Build

Use this skill for network objects and interface wiring inside an existing EVE-NG lab.

## When to Use

- Inspect current topology and network attachments
- Create or delete virtual networks
- Connect node interfaces to networks
- Check which interfaces are available on a node
- Discover available node templates before building

## Wiring Rules

- Stop affected nodes before rewiring interfaces.
- Confirm the current topology before changing links.
- Re-read topology after the change; do not trust the write response alone.
- Build through networks or bridges, not direct node-to-node links.

## MCP Server

- **Command**: `python3 -u mcp-servers/eve-ng-mcp-server/eve_ng_mcp_server.py`
- **Requires**: `EVE_URL`, `EVE_USER`, `EVE_PASSWORD`

## Available Tools

| Tool | Parameters | Purpose |
|---|---|---|
| `eve_get_topology` | `lab_path` | Full topology view |
| `eve_list_networks` | `lab_path` | List existing networks |
| `eve_create_network` | `lab_path, name, network_type?, visibility?, left?, top?` | Create a network |
| `eve_delete_network` | `lab_path, network` | Delete a network |
| `eve_list_node_interfaces` | `lab_path, node` | List node interfaces and attachments |
| `eve_connect_interface` | `lab_path, node, interface_id, network` | Connect one interface to a network |
| `eve_list_node_types` | — | List installed templates |

Networks and nodes can be referenced by **name** or **numeric ID**.

## Network Types

| Type | Use |
|---|---|
| `bridge` | Internal L2 segment |
| `ovs` | Open vSwitch bridge |
| `pnet0`–`pnet9` | Physical uplinks |
| `cloud0`–`cloud9` | Cloud or internet mapping |

## Workflow Examples

```text
"Show full topology for /Labs/bgp-demo.unl"             → eve_get_topology /Labs/bgp-demo.unl
"List networks in /Labs/bgp-demo.unl"                   → eve_list_networks /Labs/bgp-demo.unl
"Show R1 interfaces and attachments"                    → eve_list_node_interfaces /Labs/bgp-demo.unl R1
"Create bridge Net12"                                   → eve_create_network /Labs/bgp-demo.unl Net12 bridge
"Connect R1 interface 0 to Net12"                       → eve_connect_interface /Labs/bgp-demo.unl R1 0 Net12
```

## Build Flow

1. Create the lab with **eve-ng-lab-management**.
2. Add nodes with **eve-ng-node-operations**.
3. Create required networks.
4. Connect interfaces.
5. Re-read the topology.
6. Start nodes and verify with **eve-ng-console-ops**.

## Integration with Other Skills

- **eve-ng-lab-management**: create or export the lab
- **eve-ng-node-operations**: add nodes and manage stop/start windows
- **eve-ng-console-ops**: verify adjacency after wiring
- **eve-lab-topology-design**: validate the intended design before or after build

## Error Handling

| Error Code | Meaning | Resolution |
|---|---|---|
| `EVE_NOT_FOUND` | Node or network missing | Run `eve_list_networks` or `eve_list_nodes` |
| `EVE_CONFLICT` | Duplicate network name | Use a unique name |
| `EVE_VALIDATION` | Invalid type or interface reference | Re-check parameters |

## Notes

- Interface IDs are zero-based.
- `visibility=0` hides the network icon but does not disable the network.
- `left` and `top` are cosmetic canvas coordinates.
