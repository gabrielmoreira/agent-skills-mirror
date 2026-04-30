---
name: eve-ng-lab-management
description: Manage EVE-NG labs — list, inspect, create, delete, export, and check platform status.
user-invocable: true
metadata:
  openclaw:
    requires:
      bins: ["python3"]
      env: ["EVE_URL", "EVE_USER", "EVE_PASSWORD"]
---

# EVE-NG Lab Management

Use this skill for lab lifecycle work: platform health, lab inventory, lab metadata, create/delete, and `.unl` export.

## When to Use

- List labs on the EVE-NG server
- Check lab metadata before making changes
- Create a new empty lab
- Delete an unused lab
- Export a `.unl` file for backup or review
- Verify EVE-NG API health and installed images

## MCP Server

- **Command**: `python3 -u mcp-servers/eve-ng-mcp-server/eve_ng_mcp_server.py`
- **Requires**: `EVE_URL`, `EVE_USER`, `EVE_PASSWORD`
- **Optional**: `EVE_VERIFY_SSL`, `EVE_SESSION_TTL`, `EVE_HTML5`, `EVE_CONSOLE_HOST`

## Available Tools

| Tool | Parameters | Purpose |
|---|---|---|
| `eve_status` | — | Check EVE-NG version, CPU, memory, and disk |
| `eve_auth` | — | Verify API login and current user |
| `eve_list_images` | `node_type?` | List installed images |
| `eve_list_labs` | `folder?` | List labs recursively |
| `eve_get_lab` | `lab_path` | Read lab metadata |
| `eve_create_lab` | `name, folder?, description?, version?, author?` | Create an empty lab |
| `eve_delete_lab` | `lab_path` | Delete a lab |
| `eve_export_lab` | `lab_path` | Export raw `.unl` XML |

## Core Workflow

1. Check platform health with `eve_status` when behavior looks odd.
2. Locate the target lab with `eve_list_labs`.
3. Read metadata with `eve_get_lab` before changing anything.
4. Hand off to the relevant skill:
   - **eve-ng-node-operations** for node lifecycle
   - **eve-lab-topology-build** for networks and links
   - **eve-ng-console-ops** for live CLI work
   - **eve-ng-config-ops** for startup config handling

## Workflow Examples

```text
"Is EVE-NG healthy?"                    → eve_status
"List all EVE labs"                     → eve_list_labs
"Show details for /Labs/ospf-demo.unl"  → eve_get_lab /Labs/ospf-demo.unl
"Create a new lab called bgp-demo"      → eve_create_lab name=bgp-demo
"Export /Labs/bgp-demo.unl"             → eve_export_lab /Labs/bgp-demo.unl
"Delete /Labs/old-test.unl"             → eve_delete_lab /Labs/old-test.unl
```

## Integration with Other Skills

- **eve-ng-node-operations**: start, stop, create, delete, wipe nodes
- **eve-lab-topology-build**: create networks and wire interfaces
- **eve-ng-console-ops**: run CLI commands on active nodes
- **eve-ng-config-ops**: read or write startup configs
- **eve-lab-topology-design**: design or validate the topology before building

## Error Handling

| Error Code | Meaning | Resolution |
|---|---|---|
| `EVE_AUTH_FAILED` | Login failed | Check credentials |
| `EVE_NOT_FOUND` | Lab path not found | Run `eve_list_labs` |
| `EVE_CONFLICT` | Lab already exists | Choose a different name |
| `EVE_UNREACHABLE` | API is unreachable | Check `EVE_URL` and connectivity |

## Notes

- Prefer `eve_export_lab` before major topology edits.
- Use full lab paths such as `/Labs/demo.unl`.
- Deleting a lab does not replace change control or backups.
- Lab operations are environment changes; verify state before and after.
