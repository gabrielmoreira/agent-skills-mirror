---
name: mcp-server-testing
description: "Prove an MCP server works and that an agent can actually use it. Covers the Inspector, a ten-question evaluation set, and the difference between responding correctly and being usable."
lastReviewed: 2026-09-13
---

# Test an MCP Server

Two different questions. **Does it respond correctly?** is testing. **Can an agent
accomplish a task with it?** is evaluation. A server can pass the first
completely and fail the second, and the second is the one users feel.

## The Inspector

An interactive client that lists your tools, calls them with arguments you
supply, and shows the raw protocol traffic.

```bash
# TypeScript
npm run build && npx @modelcontextprotocol/inspector ./dist/server.js

# Python
python -m py_compile your_server.py
npx @modelcontextprotocol/inspector -- python your_server.py

# Any executable
npx @modelcontextprotocol/inspector /path/to/server
```

If a tool does not appear in the Inspector, no agent will see it either. Check
this before suspecting anything subtler.

## Pre-Ship Checks

- Every tool has a description saying **when** to use it, not only what it does
- Errors return actionable text with `isError: true`
- I/O is async, and paginated wherever results can grow
- Nothing writes to stdout on a stdio server
- Annotations are declared, especially `destructiveHint`
- Input schemas carry constraints, so bad input fails at the boundary

## Evaluation

Testing proves the server responds. Evaluation proves an agent can *use* it — and
it is the only way to discover that a tool description is technically accurate and
practically useless.

Write ten questions requiring real tool use, then answer each yourself so you hold
ground truth. Each question should be:

- **Independent** — not reliant on another question's answer
- **Read-only** — no destructive operations
- **Multi-step** — several tool calls and some exploration
- **Realistic** — something a person would actually ask
- **Verifiable** — one clear answer, checkable by string comparison
- **Stable** — the answer will not drift next week

```xml
<evaluation>
  <qa_pair>
    <question>Which repository had the most merged pull requests last quarter, and how many?</question>
    <answer>servers, 47</answer>
  </qa_pair>
</evaluation>
```

### Reading the results

A failure is rarely a bug. Work through these in order:

| Symptom | Usual cause |
| --- | --- |
| Agent never calls the right tool | Description says what, not when |
| Agent calls it and gets lost | Response too large, or unstructured |
| Agent gives up after an error | Error text has no recovery path |
| Agent takes ten calls for one answer | Missing a workflow tool over the raw API |

That last row is the signal `mcp-server-design` defers to: add workflow tools once
evaluations show which sequences agents keep repeating.

### Re-run on change

Run the set whenever you change a tool description or schema. A drop in answer
quality is usually a description that got vaguer, not a code regression. Treat the
evaluation set as a test suite and keep it in the repository — see
[test-driven-development](https://github.com/fabioc-aloha/Alex_ACT_ONE) for the
discipline if the project has the ACT runtime installed.

## Testing Under a Host

The Inspector is a clean room. Hosts are not. Before declaring a server done,
register it in a real host and run a task end to end. Differences that only appear
there:

- Tool-name collisions with other installed servers
- Descriptions truncated in the host's picker
- Environment variables resolved differently than in your shell
- Startup time long enough that the host gives up

## Composes With

- [mcp-server-build](../mcp-server-build/SKILL.md) — what you are testing
- [mcp-server-operations](../mcp-server-operations/SKILL.md) — for failures that
  only appear in production

## Would Revise If

- The Inspector is superseded by an official alternative.
- Teams report writing evaluation sets once and never re-running them, which
  would mean this section is documentation rather than practice and needs a
  cheaper harness.
