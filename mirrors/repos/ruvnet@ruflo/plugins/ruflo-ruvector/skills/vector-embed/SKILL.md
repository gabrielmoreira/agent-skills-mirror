---
name: vector-embed
description: Generate embeddings via npx ruvector (ONNX all-MiniLM-L6-v2, 384-dim), normalize, and store in HNSW index
argument-hint: "<text-or-file>"
allowed-tools: Bash Read mcp__claude-flow__memory_store mcp__claude-flow__memory_search
---

# Vector Embed

Generate and store vector embeddings using the `ruvector` npm package.

## When to use

Use this skill to embed text, code, or documents into 384-dimensional vectors for semantic search, similarity comparison, or clustering. ruvector uses ONNX all-MiniLM-L6-v2 with HNSW indexing (52,000+ inserts/sec, ~0.045ms search).

## Steps

1. **Ensure ruvector is available**:
   ```bash
   npm ls ruvector 2>/dev/null || npm install ruvector
   ```
2. **Embed the input**:
   - For text: `npx ruvector embed "your text here"`
   - For a file: `npx ruvector embed --file src/module.ts`
   - For batch: `npx ruvector embed --batch --glob "src/**/*.ts"`
3. **Normalization** -- ruvector L2-normalizes by default (unit sphere, cosine similarity). Alternatives: `--norm l1`, `--norm minmax`, `--norm zscore`
4. **Confirm** -- report vector ID, dimension (384), norm, and index stored in
5. **Store metadata** in AgentDB if needed:
   `mcp__claude-flow__memory_store({ key: "embed-SOURCE", value: "VECTOR_METADATA", namespace: "vector-patterns" })`

## MCP alternative

If ruvector MCP server is connected (`claude mcp add ruvector -- npx ruvector mcp start`):
- `hooks_rag_context` — semantic context retrieval
- `brain_search` — shared brain knowledge search

## Batch embedding

```bash
npx ruvector embed --batch --glob "src/**/*.ts"
```

Reports total vectors inserted and index growth.
