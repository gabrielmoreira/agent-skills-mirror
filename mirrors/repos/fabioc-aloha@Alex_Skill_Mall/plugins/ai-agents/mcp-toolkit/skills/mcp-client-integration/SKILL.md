---
name: mcp-client-integration
description: "Safely consume an MCP server someone else wrote — evaluate it before installing, register it correctly, scope its credentials, and diagnose it when it misbehaves."
lastReviewed: 2026-09-13
---

# Consume an MCP Server

Far more people install servers than write them, and installing one is the part
with the risk. **An MCP server is code that runs on your machine, holds your
credentials, and is invoked by a model that can be persuaded.** A friendly
description is not a safety property.

## Evaluate Before Installing

Five questions, cheapest disqualifier first.

**1. Who publishes it?** A vendor publishing a server for their own API has a
reputation at stake. An unaffiliated wrapper of that same API does not. Check
whether the vendor ships one before reaching for a third-party copy.

**2. What does it execute?** Read the install command. `npx some-server` fetches
and runs code at every launch, resolving to whatever the registry serves that day.
A pinned version or a vendored build is a different risk profile entirely.

**3. What credentials does it want?** A server asking for a token scoped wider
than its tools need is either careless or worse. A read-only integration should
not require write scope.

**4. What tools does it expose?** Install it, list the tools, and read them before
wiring it into anything that matters. Look for destructive operations that are not
annotated — that combination means the author did not think about the host's
ability to gate them.

**5. Is it maintained?** Last commit, open issues, whether it tracks SDK releases.
An unmaintained server pinned to an old SDK is a dependency that will break on a
protocol change nobody is watching for.

## Register It

For a Copilot plugin, declare it in `plugin.json`:

```json
{
  "mcpServers": {
    "their-server": {
      "type": "stdio",
      "command": "node",
      "args": ["node_modules/their-server/dist/index.js"],
      "env": { "THEIR_API_TOKEN": "${env:THEIR_API_TOKEN}" }
    }
  }
}
```

`${env:VAR}` reads from the environment at launch, so the token stays out of the
committed file. Restart the host after changing this block — hosts read it at
startup.

Prefer a concrete path over a package runner. `node node_modules/.../index.js`
runs what you installed and reviewed; `npx their-server` runs what the registry
serves at that moment.

## Scope the Credential

Give the server the narrowest credential that makes its tools work.

This is the one control that survives everything else going wrong. If the server
is compromised, if a prompt injection steers it, if a dependency is swapped — the
damage is bounded by what that token can do. A read-only token turns a breach into
an information disclosure instead of data loss.

Create a dedicated credential per server where the provider allows it. Shared
tokens make it impossible to tell which integration did what, and impossible to
revoke one without breaking the rest.

## Watch for Tool Shadowing

Two servers exposing a tool with the same name is a real collision, and the
resolution is host-specific. Symptoms: a tool that used to work starts doing
something else, or an agent calls the wrong backend.

After installing a second server, list the tools and look for duplicate names. If
the host offers a prefix or namespace option, use it.

## Diagnose a Misbehaving Server

| Symptom | First check |
| --- | --- |
| Server not listed | Host restarted since the config change? |
| Listed but no tools | Server crashed on startup; read the host's logs |
| Starts then exits | Server writing to stdout, corrupting the protocol |
| Works for you, not a colleague | Environment variable set in your shell only |
| Intermittent | Startup slower than the host's timeout |
| Wrong results | Tool name collision with another server |

Isolate with the Inspector, which removes the host from the equation:

```bash
npx @modelcontextprotocol/inspector node node_modules/their-server/dist/index.js
```

If it works there and not under the host, the problem is configuration or
collision, not the server.

## When to Fork

Consider vendoring or forking when the server is unmaintained but load-bearing,
when you need one tool from a server that exposes fifty, or when you must pin
behaviour a maintainer keeps changing. Forking means inheriting maintenance —
worth it only when the alternative is worse.

## Composes With

- [mcp-server-hardening](../mcp-server-hardening/SKILL.md) — the same risks from
  the author's side
- [mcp-server-design](../mcp-server-design/SKILL.md) — if evaluation concludes you
  should write your own

## Would Revise If

- A signing or provenance standard emerges for MCP servers, which would replace
  most of "evaluate before installing" with a verification step.
- Hosts add namespacing by default, making the tool-shadowing section obsolete.
