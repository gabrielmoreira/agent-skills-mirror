---
name: mcp-server-design
description: "Decide whether to build an MCP server, which protocol primitives to expose, and how to design tools an agent can actually use. Covers transports, language choice, and the tools/resources/prompts split."
lastReviewed: 2026-09-13
---

# Design an MCP Server

The design decides whether the server is usable. Everything after it is typing.

## Should This Be a Server?

Check whether one already exists. The
[servers directory](https://github.com/modelcontextprotocol/servers) lists
reference and community implementations, and most vendors with an API now ship
one.

Build your own when you are wrapping an internal API, or a third-party service
whose published server does not cover what you need. Wrapping a public API that
already has a maintained server means inheriting its maintenance burden for no
new capability.

Before designing tools, answer one question in a sentence: **what task should an
agent be able to finish that it cannot finish today?** If the answer is "call our
API", the design will drift into a thin HTTP proxy with fifty tools and no shape.

## What a Server Can Expose

Three primitives, distinguished by who decides to use them.

| Primitive | Controlled by | Use for |
| --- | --- | --- |
| **Tools** | The model | Actions the agent chooses: query, create, update |
| **Resources** | The host application | Addressable data read by URI: files, records, logs |
| **Prompts** | The user | Reusable templates a person invokes deliberately |

Most servers ship tools and stop. If everything you expose is a tool, check
whether some of it is reference data. A resource the host reads directly costs no
tool call and no round trip through the model.

Two further capabilities invert the usual direction of control. **Sampling** lets
the server ask the client for a model completion, so it can reason without
shipping its own API key. **Elicitation** lets the server ask the user for input
mid-operation. Both are in the
[specification](https://modelcontextprotocol.io/specification/); confirm your
target host supports them before designing around either.

## Choose a Transport

| Transport | Use case | Consequences |
| --- | --- | --- |
| **stdio** | Local, single user, desktop | No network, no auth, no hardening needed |
| **Streamable HTTP** | Remote, multi-tenant | Needs auth, host validation, and a deployment story |

Start with stdio unless the server must be reachable over a network. Converting
later is mostly a transport swap; tool definitions do not change. Choosing HTTP
first means paying for `mcp-server-hardening` before you have anything working.

## Choose a Language

| Language | Best for | Package |
| --- | --- | --- |
| **TypeScript** | General servers, broadest client compatibility | `@modelcontextprotocol/sdk` |
| **Python** | Data and ML pipelines | `mcp` (FastMCP) |
| **C#/.NET** | Existing .NET services | `ModelContextProtocol` |

Pick the language your service already runs in. An MCP server is a thin adapter
over logic you have; rewriting that logic in a different language to match an SDK
is the expensive way to get a worse result.

## Designing Tools

**Prefer coverage to cleverness.** When uncertain, expose the API surface rather
than guessing which workflows an agent will want. Add workflow tools once you can
see what agents actually attempt — which is what `mcp-server-testing` produces.

**Name for discovery.** A consistent prefix and an action verb:
`github_create_issue`, `github_list_repos`. An agent selects tools by reading
names and descriptions. A vague name is a tool that never gets called.

**Describe when, not just what.** "Lists repositories" tells an agent what the
tool does. "Lists repositories the authenticated user can push to; use before
creating a branch" tells it when to reach for this one instead of a neighbour.

**Return focused data.** Paginate, filter, let the caller narrow. A tool
returning a megabyte of JSON burns the agent's context and usually answers a
question nobody asked.

**Write errors an agent can act on.** `Error: check API key, verify endpoint, or
reduce page size` is recoverable. `Request failed` ends the attempt.

### Annotations

Declare these so hosts can reason about safety before calling:

| Annotation | Meaning |
| --- | --- |
| `readOnlyHint: true` | Does not modify state |
| `destructiveHint: true` | Makes irreversible changes |
| `idempotentHint: true` | Safe to retry |
| `openWorldHint: true` | Reaches an external system |

A destructive tool without `destructiveHint` is how an agent deletes something
while believing it was browsing.

## Composes With

- [mcp-server-build](../mcp-server-build/SKILL.md) — implement the design
- [mcp-server-testing](../mcp-server-testing/SKILL.md) — evaluations tell you
  which workflow tools are worth adding

## Would Revise If

- The protocol adds a primitive beyond tools, resources, and prompts, making the
  three-row table incomplete.
- A transport beyond stdio and Streamable HTTP reaches general availability.
- Teams following "prefer coverage" ship servers with so many tools that agents
  cannot choose among them, which would mean the advice needs a ceiling.
