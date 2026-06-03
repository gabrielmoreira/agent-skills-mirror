# Agent Tools DOX

## Purpose

- Own core agent tool implementations available to Agent Zero agents.
- Keep tool execution contracts, progress logging, intervention handling, and tool-result formatting stable.

## Ownership

- Tool modules in this directory are discovered by the framework and should define `Tool` subclasses.
- Shared tool base classes and response contracts live in `helpers/tool.py`.
- Plugin-specific tools belong in plugin `tools/` directories.

## Local Contracts

- Tools must derive from `helpers.tool.Tool` and implement `async def execute(...)`.
- Return `helpers.tool.Response(message=..., break_loop=...)`.
- Use `await self.agent.handle_intervention(...)` when a long-running or external result should respect pause/intervention flow.
- Sanitize or mask secrets before logging, returning, or storing tool outputs.
- Do not perform destructive filesystem or network actions without the tool contract making that behavior explicit.

## Work Guidance

- Keep tool output concise enough for message history while preserving actionable detail.
- Put reusable parsing, provider, filesystem, or network logic in `helpers/`.
- Update prompt tool instructions when changing tool names, arguments, or behavior.

## Verification

- Run targeted tool tests after changing a tool or its prompt contract.
- Run prompt/snapshot tests when tool instructions or output shape changes.

## Child DOX Index

No child DOX files.
