---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "Platform awareness for VS Code tool system: deferred tools require tool_search, external ingest provides context in remote workspaces"
application: "Always active: agents must know which tools are deferred and how to discover them"
applyTo: "**"
currency: 2026-05-18
lastReviewed: 2026-05-18
---

# Tool Awareness

## Deferred Tools (VS Code 1.118+)

Many tools are **deferred** (lazy-loaded). They appear in `availableDeferredTools` but cannot be called directly. Load via `tool_search` first with a natural-language capability description.

### Rules

1. **Search before calling.** Calling a deferred tool without loading via `tool_search` fails silently.
2. **Search once per tool.** After load, the tool stays available for the session.
3. **Use broad queries.** One broad search beats multiple narrow ones.
4. **No results means unavailable.** Don't retry with synonyms.

For common deferred tool categories and search-query patterns, see [tool-awareness-categories.instructions.md](tool-awareness-categories.instructions.md) (scoped, loads on tool/MCP/GitHub work).

## External Ingest (VS Code 1.119+)

In remote or virtual-filesystem workspaces (GitHub.dev, VS Code Remote, Codespaces), the editor provides codebase context automatically. `semantic_search` and file operations work transparently — no agent action needed.

## Would Revise If

Revise if VS Code changes the deferred-tool mechanism (e.g. `tool_search` semantics change, deferred tools become directly callable, or external-ingest changes scope in remote workspaces), or if the "search before calling" rule produces no observed failures over a quarter (the rule is no longer load-bearing because the platform changed).
