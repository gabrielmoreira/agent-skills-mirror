---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "Platform awareness for VS Code tool system: deferred tools require tool_search, external ingest provides context in remote workspaces"
application: "Always active: agents must know which tools are deferred and how to discover them"
applyTo: "**"
currency: 2026-05-05
lastReviewed: 2026-05-05
---

# Tool Awareness

## Deferred Tools (VS Code 1.118+)

Many tools are **deferred** (lazy-loaded). They appear in the `availableDeferredTools` list but cannot be called directly. Before using any deferred tool, call `tool_search` with a natural-language description of the capability you need.

### Rules

1. **Search before calling.** If a tool name appears only in `availableDeferredTools`, it must be loaded via `tool_search` first. Calling it without loading will fail silently or error.
2. **Search once per tool.** After `tool_search` returns a tool, it stays loaded for the session. Do not search again for the same tool.
3. **Use broad queries.** A single broad search (e.g., "github issues and pull requests") is more efficient than multiple narrow searches.
4. **Check availability first.** If `tool_search` returns no results for a capability, the tool is not available. Do not retry with different patterns.

### Common Deferred Tool Categories

| Category | Example tools | Search query |
| --- | --- | --- |
| GitHub operations | issues, PRs, repos, code search | "github" |
| MCP servers | Azure, Fabric, Playwright, docs | "azure" or the specific service |
| Browser automation | click, navigate, screenshot | "browser" |
| Notebook operations | run cell, edit notebook | "notebook" |
| Mermaid rendering | preview, validate diagrams | "mermaid" |

### Anti-Pattern

Do not hardcode tool names from `availableDeferredTools` without loading them. The list is informational; actual availability requires `tool_search`.

## External Ingest (VS Code 1.119+)

In remote or virtual-filesystem workspaces (e.g., GitHub.dev, VS Code Remote, Codespaces), the editor provides codebase context automatically via **external ingest**. No action needed from the agent; `semantic_search` and file operations work transparently.

This means heirs deployed to remote environments get the same codebase awareness as local workspaces without additional configuration.
