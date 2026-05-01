# Performance Patterns

## N+1 Query Detection
**Symptom:** Load a list of N items, then execute 1 query per item to fetch related data.
**Fix:** Use JOINs, `include`/`populate`, or batch queries (`WHERE id IN (...)`).
**Detection heuristic:** Look for loops containing database calls or API requests.

## Pagination
- **Never** `SELECT *` without `LIMIT` on tables that can grow unbounded.
- Use cursor-based pagination for large datasets (more stable than offset-based).
- Return `hasNextPage` and `cursor` in API responses.
- Default page size: 20–100 items. Max page size: 1000.

## Caching Strategies

| Strategy | When to Use | TTL Guidance |
|----------|-------------|-------------|
| In-memory (Map/LRU) | Single-process, small datasets | 1–5 minutes |
| Distributed (Redis) | Multi-process, shared state | 5–60 minutes |
| HTTP caching (ETag) | Static/semi-static API responses | Hours to days |
| Computed column | Expensive aggregations | Refresh on write |

**Cache invalidation:** Invalidate on write (not on timer) when data freshness matters. Use versioned cache keys for safe rollouts.

## Resource Management
- **Close connections** — database, file handles, sockets. Use `try/finally` or `using`/`with` patterns.
- **Bound queues** — set max queue depth; reject or back-pressure when full.
- **Pool connections** — reuse database/HTTP connections instead of creating per-request.
- **Clear timers** — `clearTimeout`/`clearInterval` on cleanup to prevent memory leaks.

## Algorithm Complexity Guidelines
| Acceptable | Context |
|-----------|---------|
| O(1), O(log n) | Hot paths (request handlers, real-time processing) |
| O(n) | Standard processing (list operations, single-pass transforms) |
| O(n log n) | Sorting, indexing (acceptable for moderate n) |
| O(n²) | **Flag for review** — acceptable only for small n (<1000) with justification |
| O(2^n), O(n!) | **Never in production** — refactor or approximate |
