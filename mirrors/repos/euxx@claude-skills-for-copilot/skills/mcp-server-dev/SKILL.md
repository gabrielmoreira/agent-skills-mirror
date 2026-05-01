---
name: mcp-server-dev
description: Use when the user asks to build an MCP server, create an MCP integration, wrap an API for AI agents, or expose tools via the Model Context Protocol. Guides through deployment model selection (remote HTTP, MCPB, local stdio), tool-design patterns, and framework choice before scaffolding code.
argument-hint: "[what the MCP server should connect to or expose]"
user-invocable: true
---

# Build an MCP Server

You are guiding a developer through designing and building an MCP server. MCP servers come in many forms — picking the wrong shape early causes painful rewrites later. Your first job is **discovery, not code**.

Do not start scaffolding until you have answers to the questions in Phase 1. If the user's opening message already answers them, acknowledge that and skip straight to the recommendation.

---

## Phase 1 — Interrogate the use case

Ask these questions conversationally (batch them into one message, don't interrogate one-at-a-time). Adapt wording to what the user has already told you.

### 1. What does it connect to?

| If it connects to…                              | Likely direction           |
| ----------------------------------------------- | -------------------------- |
| A cloud API (SaaS, REST, GraphQL)               | Remote HTTP server         |
| A local process, filesystem, or desktop app     | MCPB or local stdio        |
| Hardware, OS-level APIs, or user-specific state | MCPB                       |
| Nothing external — pure logic / computation     | Either — default to remote |

### 2. Who will use it?

- **Just me / my team, on our machines** → Local stdio is acceptable (easiest to prototype)
- **Anyone who installs it** → Remote HTTP (strongly preferred) or MCPB (if it _must_ be local)
- **Users who want UI widgets** → MCP app (remote or MCPB)

### 3. How many distinct actions does it expose?

This determines the tool-design pattern — see Phase 3.

- **Under ~15 actions** → one tool per action
- **Dozens to hundreds of actions** (e.g. wrapping a large API surface) → search + execute pattern

### 4. Does a tool need mid-call user input or rich display?

- **Simple structured input** (pick from list, enter a value, confirm) → **Elicitation** — spec-native, zero UI code. Host support is rolling out (Claude Code ≥ 2.1.76) — always pair with a capability check and fallback.
- **Rich/visual UI** (charts, custom pickers with search, live dashboards) → MCP app widgets — iframe-based, needs `@modelcontextprotocol/ext-apps`.
- **Neither** → plain tool returning text/JSON.

### 5. What auth does the upstream service use?

- None / API key → straightforward
- OAuth 2.0 → you'll need a remote server with CIMD (preferred) or DCR support

---

## Phase 2 — Recommend a deployment model

Based on the answers, recommend **one** path. Be opinionated. The ranked options:

### ⭐ Remote streamable-HTTP MCP server (default recommendation)

A hosted service speaking MCP over streamable HTTP. This is the **recommended path** for anything wrapping a cloud API.

**Why it wins:**

- Zero install friction — users add a URL, done
- One deployment serves all users; you control upgrades
- OAuth flows work properly (the server can handle redirects, DCR, token storage)
- Works across Claude desktop, Claude Code, Claude.ai, and third-party MCP hosts

**Choose this unless** the server _must_ touch the user's local machine.

→ **Fastest deploy:** Cloudflare Workers — zero to live URL in two commands using the official Cloudflare MCP Workers template
→ **Portable Node/Python:** Express or FastMCP, runs on any host

### Elicitation (structured input, no UI build)

If a tool just needs the user to confirm, pick an option, or fill a short form, **elicitation** does it with zero UI code. The server sends a flat JSON schema; the host renders a native form. Spec-native, no extra packages.

**Caveat:** Host support is new (Claude Code shipped it in v2.1.76; Desktop unconfirmed). The SDK throws if the client doesn't advertise the capability. Always check `clientCapabilities.elicitation` first and have a fallback.

Escalate to MCP app widgets when you need: nested/complex data, scrollable/searchable lists, visual previews, live updates.

### MCP app (remote HTTP + interactive UI)

Same as above, plus **UI resources** — interactive widgets rendered in chat. Rich pickers with search, charts, live dashboards, visual previews. Built once, renders in Claude _and_ ChatGPT.

**Choose this when** elicitation's flat-form constraints don't fit — you need custom layout, large searchable lists, visual content, or live updates. Uses `@modelcontextprotocol/ext-apps`.

Usually remote, but can be shipped as MCPB if the UI needs to drive a local app.

### MCPB (bundled local server)

A local MCP server **packaged with its runtime** so users don't need Node/Python installed. The sanctioned way to ship local servers.

**Choose this when** the server _must_ run on the user's machine — it reads local files, drives a desktop app, talks to localhost services, or needs OS-level access.

### Local stdio (npx / uvx) — _not recommended for distribution_

A script launched via `npx` / `uvx` on the user's machine. Fine for **personal tools and prototypes**. Painful to distribute: users need the right runtime, you can't push updates. Scaffold it but note the MCPB upgrade path.

---

## Phase 3 — Pick a tool-design pattern

Every MCP server exposes tools. How you carve them matters more than most people expect — tool schemas land directly in the model's context window.

### Pattern A: One tool per action (small surface)

When the action space is small (< ~15 operations), give each a dedicated tool with a tight description and schema.

```
create_issue    — Create a new issue. Params: title, body, labels[]
update_issue    — Update an existing issue. Params: id, title?, body?, state?
search_issues   — Search issues by query string. Params: query, limit?
add_comment     — Add a comment to an issue. Params: issue_id, body
```

**Why it works:** The model reads the tool list once and knows exactly what's possible. No discovery round-trips. Each tool's schema validates inputs precisely.

### Pattern B: Search + execute (large surface)

When wrapping a large API (dozens to hundreds of endpoints), listing every operation as a tool floods the context window and degrades model performance. Instead, expose **two** tools:

```
search_actions  — Given a natural-language intent, return matching actions
                  with their IDs, descriptions, and parameter schemas.
execute_action  — Run an action by ID with a params object.
```

The server holds the full catalog internally. The model searches, picks, executes. Context stays lean.

**Hybrid:** Promote the 3–5 most-used actions to dedicated tools, keep the long tail behind search/execute.

---

## Phase 4 — Pick a framework

Recommend one of these two. Others exist but these have the best MCP-spec coverage.

| Framework                                                 | Language | Use when                                                                                                                                                                      |
| --------------------------------------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Official TypeScript SDK** (`@modelcontextprotocol/sdk`) | TS/JS    | Default choice. Best spec coverage, first to get new features.                                                                                                                |
| **FastMCP 3.x** (`fastmcp` on PyPI)                       | Python   | User prefers Python, or wrapping a Python library. Decorator-based, low boilerplate. This is jlowin's package — not the frozen FastMCP 1.0 bundled in the official `mcp` SDK. |

If the user already has a language/stack in mind, go with it — both produce identical wire protocol.

---

## Phase 5 — Scaffold and implement

Once you've settled the four decisions (deployment model, tool pattern, framework, auth), implement accordingly:

1. **Remote HTTP, no UI** → Scaffold a minimal server using the chosen framework. For TypeScript SDK: create a `Server` instance, register tools with `server.tool(name, schema, handler)`, wrap in a Hono/Express app with `streamableHttpHandler`. For FastMCP: use `@mcp.tool()` decorators. For Cloudflare Workers deployment, use the `workers-mcp` template from Cloudflare.
2. **MCP app (UI widgets)** → Scaffold the remote HTTP server first, then add `@modelcontextprotocol/ext-apps` for iframe-based widget resources. Each widget binds to one tool.
3. **MCPB (bundled local)** → Scaffold the stdio server, then package with the MCPB packaging guide (bundles runtime so users don't need Node/Python installed).
4. **Local stdio prototype** → Scaffold the simplest case; use `StdioServerTransport` (TS) or `fastmcp.run()` with `transport="stdio"`. Flag MCPB as the distribution upgrade path.

When scaffolding, produce complete, runnable code. Do not leave placeholder TODOs for the core transport or tool registration.

---

## Beyond tools — the other primitives

Tools are one of three server primitives. Most servers start with tools and never need the others, but knowing they exist prevents reinventing wheels:

| Primitive       | Who triggers it      | Use when                                      |
| --------------- | -------------------- | --------------------------------------------- |
| **Resources**   | Host app (not model) | Exposing docs/files/data as browsable context |
| **Prompts**     | User (slash command) | Canned workflows ("/summarize-thread")        |
| **Elicitation** | Server, mid-tool     | Asking user for input without building UI     |
| **Sampling**    | Server, mid-tool     | Need LLM inference in your tool logic         |

---

## Quick reference: decision matrix

| Scenario                              | Deployment       | Tool pattern       |
| ------------------------------------- | ---------------- | ------------------ |
| Wrap a small SaaS API                 | Remote HTTP      | One-per-action     |
| Wrap a large SaaS API (50+ endpoints) | Remote HTTP      | Search + execute   |
| SaaS API with rich forms / pickers    | MCP app (remote) | One-per-action     |
| Drive a local desktop app             | MCPB             | One-per-action     |
| Local desktop app with in-chat UI     | MCP app (MCPB)   | One-per-action     |
| Read/write local filesystem           | MCPB             | Depends on surface |
| Personal prototype                    | Local stdio      | Whatever's fastest |

---

## Reference resources

- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) — official SDK with examples and type definitions
- [FastMCP (jlowin)](https://github.com/jlowin/fastmcp) — Python framework; use v3.x from PyPI, not the frozen 1.0 in `mcp` SDK
- [Cloudflare workers-mcp](https://github.com/cloudflare/workers-mcp) — fastest remote deploy path
- [MCP Specification](https://modelcontextprotocol.io/specification) — elicitation, resources, prompts, server capabilities, auth flows
