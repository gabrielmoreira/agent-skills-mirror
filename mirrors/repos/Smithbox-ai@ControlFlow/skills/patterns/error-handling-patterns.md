# Error Handling Patterns

## Error Classification (aligned with Orchestrator failure taxonomy)

| Classification | Meaning | Response |
|---------------|---------|----------|
| `transient` | Temporary failure (network, rate limit, flaky) | Retry with exponential backoff + jitter |
| `fixable` | Correctable issue (typo, missing import, bad config) | Fix and retry immediately |
| `needs_replan` | Architecture mismatch, missing dependency | Escalate to planner for redesign |
| `escalate` | Security risk, data integrity, unresolvable | Stop and await human decision |

## Boundary Validation
- **Validate at system boundaries** — function entry points, API handlers, file I/O, user input.
- **Trust internally** — once validated at the boundary, inner functions can assume valid data.
- **Fail fast** — reject invalid input immediately with a clear error message.

## Retry Patterns

### Exponential Backoff with Jitter
```
delay = min(base_delay × 2^attempt + random_jitter, max_delay)
```
- Base delay: 100ms. Max delay: 30s. Max attempts: 3–5.
- Jitter prevents thundering herd on shared resources.

### Retry Decision Table
| Error Type | Retry? | Strategy |
|-----------|--------|----------|
| Network timeout | Yes | Exponential backoff |
| HTTP 429 (rate limit) | Yes | Respect `Retry-After` header |
| HTTP 4xx (client error) | No | Fix the request |
| HTTP 5xx (server error) | Yes | Exponential backoff (max 3) |
| Validation error | No | Fix the input |
| Auth error | No | Re-authenticate or escalate |

## Error Propagation
- **Wrap errors with context** — add "what was being attempted" to error messages.
- **Don't swallow errors** — catch only when you can handle; re-throw otherwise.
- **Preserve stack traces** — use `cause` chaining (e.g., `new Error('message', { cause: originalError })`).
- **Log at the boundary** — log once at the outermost handler, not at every layer.
