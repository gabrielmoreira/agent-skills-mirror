---
name: vector-search
description: HNSW vector search with RuVector embeddings for 150x-12500x faster semantic retrieval
allowed-tools: mcp__claude-flow__embeddings_generate mcp__claude-flow__embeddings_search mcp__claude-flow__embeddings_compare mcp__claude-flow__embeddings_init mcp__claude-flow__embeddings_status mcp__claude-flow__embeddings_hyperbolic mcp__claude-flow__embeddings_neural mcp__claude-flow__ruvllm_hnsw_create mcp__claude-flow__ruvllm_hnsw_add mcp__claude-flow__ruvllm_hnsw_route mcp__claude-flow__memory_search_unified Bash
---

# Vector Search

HNSW-indexed vector search with RuVector embeddings (384-dim ONNX).

## When to use

When you need fast semantic search across large knowledge bases. HNSW provides 150x-12,500x faster search compared to brute-force scanning.

## Steps

1. **Check status** — call `mcp__claude-flow__embeddings_status` to verify the embedding engine
2. **Initialize** — call `mcp__claude-flow__embeddings_init` if not already active
3. **Generate embeddings** — call `mcp__claude-flow__embeddings_generate` for text input
4. **Search** — call `mcp__claude-flow__embeddings_search` with a query for semantic matches
5. **Compare** — call `mcp__claude-flow__embeddings_compare` to measure similarity between texts
6. **Unified search** — call `mcp__claude-flow__memory_search_unified` to search across all namespaces

## HNSW Index

For building custom HNSW indexes:
- `mcp__claude-flow__ruvllm_hnsw_create` — create a new index
- `mcp__claude-flow__ruvllm_hnsw_add` — add vectors to the index
- `mcp__claude-flow__ruvllm_hnsw_route` — route queries through the index

## Hyperbolic embeddings

For hierarchical data (code trees, org charts), use `mcp__claude-flow__embeddings_hyperbolic` which maps to Poincare ball space.

## CLI alternative

```bash
npx @claude-flow/cli@latest embeddings search --query "authentication patterns"
npx @claude-flow/cli@latest embeddings init
npx @claude-flow/cli@latest memory search --query "your query"
```

## Performance

| Method | Speed |
|--------|-------|
| Brute-force scan | Baseline |
| HNSW (n=500) | 150x faster |
| HNSW (n=10,000) | 12,500x faster |
