---
name: reasonix-guide
description: "Diagnose missing or misconfigured Reasonix skills, commands, hooks, MCP servers, plugins, and instructions."
runAs: inline
---

# Reasonix capability diagnostics

For a loading or configuration problem, start with the relevant section of
`reasonix doctor capabilities --json`. This static report starts no MCP
subprocesses and makes no network calls. Use its issue codes, sources, and
remediations; a configuration question with enough evidence needs no full report.

## References

Read only the page needed for the reported capability. These files are bundled
in the binary; a `(builtin:...)` source is not a local filesystem path.

| Capability | Reference |
| --- | --- |
| Skill discovery, priority, overrides | [skills](references/skills.md) |
| Slash command naming and overrides | [commands](references/commands.md) |
| Hook events, matching, timeouts | [hooks](references/hooks.md) |
| MCP sources, transport, startup | [MCP](references/mcp.md) |
| Plugin manifests and loading | [plugins](references/plugins.md) |
| Standing instruction scope and imports | [instructions](references/instructions.md) |

Read a page using `read_skill` with `name="reasonix-guide"` and
`reference="references/skills.md"` (substitute the page path). If the tool is
not directly exposed, use:

```json
{"action":"call","capability_id":"tool:read_skill","arguments":{"name":"reasonix-guide","reference":"references/skills.md"}}
```

## Runtime and permissions

Desktop Settings → Diagnostics opens a static report. Refresh repeats collection;
the optional session-runtime view reads the active tab Host without starting MCP.
The page can copy redacted JSON and link to the relevant settings tab; it never
auto-edits config, executes hooks, or reconnects servers.

Live probing runs third-party code and may send configured environment/headers.
Use `reasonix doctor capabilities --live --timeout 5s --json` only when starting
those servers is explicitly authorized in the session. A diagnostic request
alone does not authorize configuration changes.

Keep tokens, header/env values, URL query strings, usernames, and external
machine paths out of reports. Use `<workspace>/…`, `~/…`, or `<external>/…`.
