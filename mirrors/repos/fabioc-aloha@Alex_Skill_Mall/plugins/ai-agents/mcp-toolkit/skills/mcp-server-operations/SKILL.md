---
name: mcp-server-operations
description: "Ship, version, and run an MCP server after it works — packaging and distribution, breaking-change discipline, deployment shapes, and debugging failures that only appear under a host."
lastReviewed: 2026-09-13
---

# Operate an MCP Server

Everything after the server works on your machine.

## Distribution

How people get it determines how they upgrade it.

| Shape | Install | Upgrade path |
| --- | --- | --- |
| **npm / PyPI / NuGet package** | Registry install, pinned version | User bumps the pin |
| **Repository + local build** | Clone and build | User pulls |
| **Container image** | Pull a tag | Retag and repull |
| **Bundled in a plugin** | Arrives with the plugin | Plugin release |

Publishing to a registry is the only shape where a consumer can pin a version and
know what they are running. A server installed from a branch is a server whose
behaviour changes without anyone deciding it should.

## Versioning

A tool signature is an API. Agents bind to names and schemas, and prompts written
against your tools are code you do not control.

**Breaking**, needs a major version:

- Removing a tool, or renaming one
- Removing a parameter, or making an optional one required
- Narrowing an accepted value range
- Changing the shape of a returned payload consumers parse

**Not breaking**:

- Adding a tool
- Adding an optional parameter
- Widening an accepted range
- Improving a description

That last one deserves emphasis: descriptions are the agent's interface, and
improving them is both safe and the highest-leverage change you can ship. Most
"the server got worse" reports are a description that drifted vaguer.

Keep a changelog a consumer can read before upgrading. "Various improvements"
tells someone running it in production nothing.

## Deployment Shapes

| Transport | Where it runs | Operational burden |
| --- | --- | --- |
| stdio | On the user's machine, launched by the host | None — the host owns the lifecycle |
| HTTP | A service you deploy | Everything: uptime, scaling, certificates, auth |

Choosing HTTP means signing up to run a service. Choose it when the server must
be reachable by many users or hold central state — not because it felt more
modern.

For HTTP, prefer stateless sessions. Stateless servers scale horizontally and
survive restarts without coordination; stateful ones need session affinity, which
is a load-balancer problem you inherit forever.

## Observability

You cannot attach a debugger to a server a host launched. Build in the signal.

- **Log to stderr** on stdio, always. It is the only channel that does not corrupt
  the protocol
- **Log tool name, duration, and outcome** for every call. Most production
  questions are "which tool is slow" or "which tool is failing"
- **Never log arguments verbatim** — they carry user data and sometimes secrets
- **Emit a startup line** with version and tool count. It is the fastest way to
  confirm which build a host actually loaded

## Debugging Under a Host

Failures that never appear in the Inspector:

| Symptom | Likely cause |
| --- | --- |
| Server absent from the host | Config added to a running session; restart the host |
| Starts then immediately exits | stdout pollution corrupting the handshake |
| Works locally, not for a colleague | Environment variable resolved from your shell only |
| Intermittent disappearance | Startup slower than the host's timeout |
| Tool shadowed | Name collision with another installed server |

Work from the host's own logs first. A server that never started leaves no logs of
its own, and the absence is the evidence.

## Deprecating a Tool

Removing a tool breaks prompts you cannot see. Stage it:

1. Mark it deprecated in the description, naming the replacement
2. Ship a minor version; consumers see the notice when they read the tools
3. Remove it in the next major, with the changelog naming the replacement again

An agent reading "deprecated, use `list_items_v2`" will usually route itself.
That is a property of the description-driven interface worth using deliberately.

## Composes With

- [mcp-server-testing](../mcp-server-testing/SKILL.md) — re-run evaluations before
  each release
- [mcp-server-hardening](../mcp-server-hardening/SKILL.md) — before any HTTP
  deployment

## Would Revise If

- A registry emerges as the standard distribution channel for MCP servers, which
  would collapse the four-row distribution table to one recommended path.
- Hosts begin surfacing server logs directly, making the debugging table obsolete.
