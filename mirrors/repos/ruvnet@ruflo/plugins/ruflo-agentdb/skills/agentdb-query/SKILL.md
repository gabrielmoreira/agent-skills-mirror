---
name: agentdb-query
description: Query AgentDB with semantic routing, hierarchical recall, causal graphs, and context synthesis
allowed-tools: mcp__claude-flow__agentdb_semantic-route mcp__claude-flow__agentdb_hierarchical-recall mcp__claude-flow__agentdb_hierarchical-store mcp__claude-flow__agentdb_context-synthesize mcp__claude-flow__agentdb_causal-edge mcp__claude-flow__agentdb_pattern-search mcp__claude-flow__agentdb_pattern-store mcp__claude-flow__agentdb_controllers mcp__claude-flow__agentdb_health mcp__claude-flow__agentdb_batch mcp__claude-flow__agentdb_feedback mcp__claude-flow__agentdb_consolidate mcp__claude-flow__agentdb_session-start mcp__claude-flow__agentdb_session-end Bash
---

# AgentDB Query

Query and manage AgentDB's 19 memory controllers.

## When to use

When you need to store, retrieve, or search knowledge across agent sessions. AgentDB provides hierarchical storage, causal knowledge graphs, semantic routing, and context synthesis.

## Steps

1. **Check health** — call `mcp__claude-flow__agentdb_health` to verify AgentDB is running
2. **Start session** — call `mcp__claude-flow__agentdb_session-start` if not already active
3. **Store knowledge** — call `mcp__claude-flow__agentdb_hierarchical-store` for structured data
4. **Recall knowledge** — call `mcp__claude-flow__agentdb_hierarchical-recall` with a query
5. **Search patterns** — call `mcp__claude-flow__agentdb_pattern-search` for learned patterns
6. **Synthesize context** — call `mcp__claude-flow__agentdb_context-synthesize` to combine multiple memories
7. **Build causal graph** — call `mcp__claude-flow__agentdb_causal-edge` to link related knowledge

## 19 Controllers

Call `mcp__claude-flow__agentdb_controllers` to list all available controllers:
- Hierarchical store/recall
- Pattern store/search
- Semantic routing
- Context synthesis
- Causal edges
- Feedback loops
- Batch operations
- Consolidation

## CLI alternative

```bash
npx @claude-flow/cli@latest memory search --query "your query" --namespace patterns
npx @claude-flow/cli@latest memory store --key "key" --value "value" --namespace patterns
npx @claude-flow/cli@latest memory list --namespace patterns
```
