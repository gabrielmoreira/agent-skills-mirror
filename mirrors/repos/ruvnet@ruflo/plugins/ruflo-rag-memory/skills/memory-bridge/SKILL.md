---
name: memory-bridge
description: Bridge Claude Code auto-memory into AgentDB with ONNX vector embeddings
allowed-tools: mcp__claude-flow__memory_import_claude mcp__claude-flow__memory_bridge_status mcp__claude-flow__memory_search_unified Bash(npx *)
---
Import Claude Code memories into AgentDB for semantic search across sessions.

Via MCP:
- Import current project: `mcp__claude-flow__memory_import_claude({})`
- Import all projects: `mcp__claude-flow__memory_import_claude({ allProjects: true })`
- Check health: `mcp__claude-flow__memory_bridge_status({})`
- Unified search: `mcp__claude-flow__memory_search_unified({ query: "QUERY", limit: 5 })`

The bridge auto-imports on `session-start`. Memories get 384-dim ONNX embeddings (all-MiniLM-L6-v2) for cross-namespace unified search.

Results include source attribution: `claude-code`, `auto-memory`, or `agentdb`.
