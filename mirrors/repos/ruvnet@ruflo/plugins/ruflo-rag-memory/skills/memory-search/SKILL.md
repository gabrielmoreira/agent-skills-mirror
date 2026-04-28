---
name: memory-search
description: Semantic search across Ruflo AgentDB with HNSW vector indexing
allowed-tools: mcp__claude-flow__memory_search mcp__claude-flow__memory_store mcp__claude-flow__memory_list mcp__claude-flow__memory_retrieve Bash(npx *)
argument-hint: "[query]"
---
Search memory with semantic vector search (150x-12,500x faster than brute force).

Via MCP: `mcp__claude-flow__memory_search({ query: "authentication patterns", namespace: "patterns", limit: 5 })`

Store: `mcp__claude-flow__memory_store({ key: "pattern-name", value: "what worked", namespace: "patterns" })`

List: `mcp__claude-flow__memory_list({ namespace: "patterns", limit: 10 })`

Retrieve: `mcp__claude-flow__memory_retrieve({ key: "pattern-name", namespace: "patterns" })`

Common namespaces: `patterns`, `tasks`, `solutions`, `feedback`, `security`.
