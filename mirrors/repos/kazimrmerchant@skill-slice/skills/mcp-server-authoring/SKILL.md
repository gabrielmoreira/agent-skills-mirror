---
name: mcp-server-authoring
version: 1.0.1
description: "Designs and implements Model Context Protocol servers from scratch: tools, resources, prompts, stdio and Streamable HTTP transports, JSON Schema, errors, Inspector testing, and packaging. Use when creating an MCP server or exposing a local API or CLI to Cursor or Claude. Not for writing SKILL.md files (create-skill) or only editing a host's MCP JSON without implementing a server."
risk: safe
source: opus-skills-library
date_added: 2026-07-15
---

# MCP Server Authoring

Build production-quality Model Context Protocol servers: correct protocol usage, model-friendly tool design, robust transports, and safe packaging. This is the **authoring** skill. For installing a finished server into Cursor, compose with the `mcp-cursor-integration` skill.

## When to Use

- You are creating a new MCP server from scratch or adding significant features to an existing one.
- You need to design tool descriptors, resources, or prompts for an MCP server.
- You are exposing a local API, CLI, or dataset to Cursor/Claude via MCP.
- You need guidance on transport selection (stdio vs Streamable HTTP), language choice (TypeScript vs Python), or packaging.
- Trigger keywords: "MCP server", "Model Context Protocol", "tool descriptor", "MCP transport", "MCP schema", "expose API to Cursor".

## Prerequisites

- Node.js (for TypeScript servers) or Python 3.10+ (for Python servers).
- For Windows hosts (primary): PowerShell as the default shell. Use full absolute paths to `node`/`python` because GUI-launched hosts do not inherit your shell PATH.
- `npx` available for running the MCP Inspector.
- Basic familiarity with JSON-RPC 2.0 and JSON Schema.

## Bundled references (read on demand, not all at once)

| File | Load when |
|---|---|
| `reference.md` | You need protocol details: lifecycle, transports, error codes, pagination, versioning, Windows issues, anti-patterns. |
| `typescript-server-template.md` | Building a server in Node/TypeScript. |
| `python-server-template.md` | Building a server in Python. |
| `security-checklist.md` | Before shipping ANY server. Mandatory for servers that touch files, shells, networks, or secrets. |
| `examples.md` | You want worked end-to-end examples and bad→good tool-design comparisons. |

## Overview

MCP is JSON-RPC 2.0 between a **host** (Cursor, Claude Desktop, Claude Code), which runs an MCP **client** per connection, and your **server**. The server exposes three primitives:

- **Tools** — model-invoked functions (`tools/list`, `tools/call`). The workhorse. Each has a name, description, JSON Schema `inputSchema`, optional `outputSchema` and behavioral `annotations`.
- **Resources** — application-controlled read-only data (`resources/list`, `resources/read`), addressed by URI; `ResourceTemplate` for parameterized URIs.
- **Prompts** — user-invoked message templates (`prompts/list`, `prompts/get`), surfaced as slash commands in some hosts.

Clients may additionally offer **sampling** (server asks the client's LLM), **roots** (workspace folders), and **elicitation** (server asks the user for input). Never depend on these — check negotiated capabilities.

Lifecycle: `initialize` (version + capability negotiation) → `notifications/initialized` → normal traffic → shutdown. Current protocol revision family: `2025-06-18` (structured tool output, elicitation, no JSON-RPC batching); hosts still commonly speak `2025-03-26` and `2024-11-05`. SDKs negotiate this for you — pin a recent SDK and don't hand-roll.

## Procedure

### Step 1 — Choose transport: stdio vs Streamable HTTP

| | **stdio** (default) | **Streamable HTTP** |
|---|---|---|
| Process model | Host spawns your process per client | You run a service; many clients connect |
| Users | Single local user | Remote / shared / multi-user |
| Auth | Inherits local user; env vars for API keys | Required: OAuth 2.1 / bearer at minimum |
| State | Trivial (one process = one session) | Sessions via `mcp-session-id` header |
| Ops burden | None | TLS, origin checks, scaling, monitoring |

**Rule: local integration (files, local DBs, dev tools, wrapping a CLI) → stdio. Hosted multi-tenant service → Streamable HTTP.** Plain HTTP+SSE ("SSE transport") is the deprecated 2024-11-05 pattern; implement Streamable HTTP instead and let the SDK provide SSE-compat if a host needs it. Never build both from scratch — write transport-agnostic server logic and bind a transport at the entry point.

### Step 2 — Choose language

- **TypeScript** (`@modelcontextprotocol/sdk` + `zod`): best host compatibility surface, `npx` distribution, single-file `dist` deploys. Use for anything users will install.
- **Python** (`mcp` package, FastMCP API): fastest authoring (decorators + type hints generate schemas), `uv`/`uvx` distribution. Use when the capability lives in the Python ecosystem (data, ML, science libs).

### Step 3 — Design tools first, code second

1. List the *user outcomes*, not the API endpoints. 3–10 outcome-shaped tools beat 40 endpoint-shaped ones.
2. Write every tool's name, one-paragraph description, and schema in a doc before implementing.
3. Tool names: `snake_case`, `verb_noun` (`search_issues`, `create_invoice_draft`). Unique meaning per name — if two tools' descriptions could be confused, merge or rename.
4. Descriptions are prompts. Write for the model: what it does, when to use it (and when NOT to), what it returns, hard limits. One dense paragraph beats bullet fluff.
5. Schemas: JSON Schema draft 2020-12. Describe every property; use `enum` for closed sets, `default` for optionals, `required` accurately; prefer flat objects over nested `oneOf`/`anyOf` (host support is uneven). Keep ≤ ~7 top-level params; more means the tool is doing too much.
6. Annotations (untrusted hints, but hosts use them for confirmation UX): `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`. Never mark a mutating tool `readOnlyHint: true`.
7. Idempotency: make mutating tools idempotent where possible (upsert semantics, client-supplied idempotency keys). Hosts and models retry.
8. Result size discipline: return summaries + IDs + `nextCursor` pagination, not blobs. Truncate with an explicit marker and a way to fetch more. Large artifacts → write to a file/resource and return the URI (resource links).
9. Errors as content: tool *execution* failures return `isError: true` with an actionable text message (what failed + what the model should try instead). Reserve JSON-RPC errors for protocol-level problems (unknown tool, invalid params). A raised exception that becomes "Internal error" teaches the model nothing.
10. Long work: report `notifications/progress` when a `progressToken` is given; honor cancellation; never block the transport thread/loop.

### Step 4 — Scaffold from the matching template

- TypeScript: load `typescript-server-template.md`.
- Python: load `python-server-template.md`.

### Step 5 — Implement handlers

1. Validate inputs against the schema.
2. Enforce limits (timeouts, result size, rate limits).
3. Return small, structured results.

### Step 6 — Validate descriptors

- Names match `^[a-zA-Z0-9_-]{1,64}$`.
- Every schema property has a `description`.
- Enums used for closed sets.
- `annotations` set honestly (see Step 3).

### Step 7 — Test

1. Run MCP Inspector:

```powershell
npx @modelcontextprotocol/inspector
```

2. Call every tool happy-path + one invalid-input path.
3. Run in-memory unit tests (both templates show how).

### Step 8 — Run the security checklist

Load `security-checklist.md` and complete it. This is a non-negotiable gate before shipping.

### Step 9 — Package & install

1. Templates cover `package.json`/`pyproject.toml`, bin entry points, and Cursor `mcp.json` snippets.
2. For deeper Cursor wiring, compose with the `mcp-cursor-integration` skill.
3. Version your server (`1.0.0`), package it, write the install snippet, and test in a real host.

## Pitfalls

### The one fatal stdio rule

**stdout is the wire.** In a stdio server, anything printed to stdout that isn't a JSON-RPC frame corrupts the session (typically a silent client disconnect or JSON parse error at startup).

- TypeScript: `console.log` → forbidden; use `console.error` (stderr) or `server.sendLoggingMessage(...)`.
- Python: `print()` → forbidden; configure `logging` to stderr or use `ctx.info()/ctx.warning()`.
- Also police your *dependencies*: banner-printing libs, `pip` warnings, debuggers, and Node deprecation warnings all write to stdout/stderr — verify stdout stays clean by piping it through a JSON validator during a smoke test.

### Top anti-patterns (full catalogue in `reference.md`)

1. **Endpoint mirroring** — one tool per REST endpoint. Design for tasks.
2. **Blob dumping** — multi-MB tool results that eat the context window.
3. **Blocking tools** — synchronous 5-minute calls with no progress or timeout.
4. **stdout pollution** — see above; the #1 "my server doesn't work in Cursor" cause.
5. **Vague descriptions** — "Manages items." The model will misuse or ignore the tool.
6. **Secrets in descriptors or results** — descriptors are sent to every client and often logged.
7. **Trusting fetched content** — text your tool returns from the outside world is prompt-injection surface; sanitize/label it (see `security-checklist.md`).
8. **Hand-rolled protocol** — reimplementing framing/lifecycle instead of using the SDK.

### Windows quick notes (details in `reference.md`)

- Use absolute paths in `mcp.json` with `\\` escaping.
- Wrap `npx`/`uvx` as `"command": "cmd", "args": ["/c", "npx", ...]` when direct spawn fails.
- Set `PYTHONUTF8=1` for Python servers.
- GUI-launched hosts don't inherit your shell PATH — prefer full paths to `node`/`python` or use absolute script paths.

## Verification

### Definition of done

- [ ] Tools documented (name/description/schema) and reviewed against the design rules in Step 3.
- [ ] Inspector session: every tool called happy-path + one invalid-input path.
- [ ] stdout-cleanliness smoke test passed (stdio) / origin+auth configured (HTTP).
- [ ] `security-checklist.md` completed.
- [ ] Versioned (`1.0.0`), packaged, install snippet written and tested in a real host.

### Checkable commands

**Inspector smoke test (PowerShell):**

```powershell
npx @modelcontextprotocol/inspector node dist/index.js
```

**stdout cleanliness check (stdio servers) — pipe output through a JSON validator:**

```powershell
node dist/index.js | ForEach-Object { try { $_ | ConvertFrom-Json | Out-Null } catch { Write-Host "NON-JSON STDOUT: $_" } }
```

Any "NON-JSON STDOUT" line means stdout pollution — fix before shipping.

**Descriptor name validation (PowerShell):**

```powershell
$names = @("search_issues", "create_invoice_draft", "Bad Name!", "tool")
foreach ($n in $names) { if ($n -match '^[a-zA-Z0-9_-]{1,64}$') { Write-Host "OK: $n" } else { Write-Host "INVALID: $n" } }
```

## Related skills

- `mcp-cursor-integration` — install a finished MCP server into Cursor, configure `mcp.json`, and debug connection issues.
