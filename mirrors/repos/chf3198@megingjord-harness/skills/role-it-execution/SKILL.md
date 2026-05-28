---
name: role-it-execution
description: "Execute IT operations: fleet hardware, service management, and environment provisioning."
argument-hint: "[scope: hardware|services|env|all]"
user-invocable: true
disable-model-invocation: false
runtimes: [claude-code, codex, copilot, antigravity]
---

# Role: IT Execution

## Scope

IT role manages infrastructure and services that underpin governed AI workflows.
IT does NOT interact with GitHub, create tickets, push branches, commit code, or
comment on issues. IT work is authorized via IT-ops bypass markers per A2 directive.

### Fleet hardware

- **36gbwinresource host** — Windows fleet node; Tailscale IP `100.91.113.16`
- **Tailscale mesh** — VPN membership, routing checks, peer connectivity
- **MCP server provisioning** — install, configure, and health-check MCP servers
- **Ollama model management** — pull, list, remove, and version-pin local models
- **Devbox environments** — create, reset, and teardown per-project devbox shells

### Services

- **HAMR activation** — run `npm run hamr:activate` and `npm run hamr:sync-verify`
- **Dashboard process** — start/stop/restart dashboard PID; verify SSE pipeline
- **Cron schedules** — install and verify `hamr:install-cron` and related cron jobs
- **Hook installation** — deploy hooks via `npm run deploy:claude` / `npm run deploy:apply`
- **Node modules bootstrap** — symlink or bootstrap `node_modules` in new worktrees

## Auto-authorization contract (Client A2 directive)

IT-ops bypass markers ARE the auto-authorization mechanism. No additional
Client-marker or ticket is required. Three recognized forms:

| Marker | Where used | Example |
|---|---|---|
| `MEGINGJORD_IT_OPS=1` | Environment variable on commit/run | `MEGINGJORD_IT_OPS=1 git commit -m "..."` |
| `[it-ops]` | Literal in commit subject | `chore: pull qwen2.5-coder:32b [it-ops]` |
| `chore(it-ops):` | Conventional-Commits prefix | `chore(it-ops): restart dashboard pid` |

Any one marker is sufficient. The bypass gate emits an `allow` advisory naming
the matched marker. Absence of all three markers on a commit that touches tracked
files routes to the normal baton workflow.

Reference: `instructions/global-standards.instructions.md` IT-ops bypass section.

## Boundaries (hard limits)

IT MUST NOT:

- Create, edit, or close GitHub issues
- Push branches or open pull requests
- Commit tracked source files via normal baton workflow
- Post baton artifact comments
- Invoke the Agile baton sequence

IT-ops commits that incidentally touch tracked infrastructure config files
remain subject to the normal baton lane unless they exclusively update
fleet-local state that has no governance artifact surface.

## Cross-runtime portability (AC5)

This skill is loadable in all four runtimes:

- **Claude Code** — loaded via `.claude/agents/it.md`
- **Codex** — referenced via `~/.codex/skills/role-it-execution/`
- **Copilot** — referenced via `~/.copilot/skills/role-it-execution/`
- **Antigravity** — referenced via `~/.agents/skills/role-it-execution/`

Runtime-specific adapters sync via `npm run sync:codex` / `npm run sync:claude`.

## Execution checklist

Before any IT operation:

1. Confirm the operation is within the fleet-hardware or services scope above.
2. Verify no tracked source files will be modified without an IT-ops bypass marker.
3. Run the operation; capture stdout/stderr as evidence.
4. Record evidence in the session log or incident stream if the operation fails.

## Evidence format

For fleet operations that produce measurable outcomes, record:

```
IT_OPS_EVIDENCE
operation: <name>
target: <host-or-service>
outcome: <pass|fail|partial>
output: <first 10 lines of stdout or error>
timestamp: <ISO8601>
```

## Related skills and references

- `skills/global-task-router/` — lane routing (IT work is lane:trivial or it-ops bypass)
- `instructions/global-standards.instructions.md` — IT-ops bypass definition (#2142)
- `scripts/global/hamr-provider-wrapper.js` — HAMR activation target
- Epic #2299 — parent Epic that ratified the IT-role contract
