---
name: api-design
description: Backend API design specialist. Use when building REST/GraphQL APIs, designing endpoints, data models, or backend architecture. Covers RESTful principles, HTTP semantics, error handling, versioning, and OWASP-aligned security.
---

<!--
  Source: wshobson/agents (backend-development plugin)
  File:   https://github.com/wshobson/agents/tree/main/plugins/backend-development/skills/api-design-principles
  Used by: builder agent (backend)
-->

# API Design Principles

## When to trigger
- Designing a new API endpoint
- Adding routes to existing API
- Database schema work that affects API contract
- Keywords: "endpoint", "API", "route", "backend", "server", "REST", "GraphQL"

## Core RESTful principles

### Resource-oriented URLs
- Nouns, not verbs: `/users/123`, not `/getUser?id=123`
- Pluralize resources: `/orders`, not `/order`
- Nest only when expressing parent/child: `/users/:id/orders`
- Max 2 levels deep — beyond that, use query params

### HTTP methods (correct semantics)
| Method | Use for | Idempotent | Safe |
|--------|---------|------------|------|
| GET    | Read    | Yes        | Yes  |
| POST   | Create  | No         | No   |
| PUT    | Replace (full update) | Yes | No |
| PATCH  | Partial update | No* | No |
| DELETE | Remove  | Yes        | No   |

\* PATCH can be idempotent depending on semantics.

### Status codes (correct use)
- **200** OK — successful GET/PUT/PATCH with body
- **201** Created — successful POST creating resource
- **204** No Content — successful DELETE or action with no body
- **400** Bad Request — validation failure
- **401** Unauthorized — missing/invalid auth
- **403** Forbidden — authenticated but not authorized
- **404** Not Found — resource doesn't exist
- **409** Conflict — version mismatch, duplicate resource
- **422** Unprocessable Entity — semantic validation failure
- **429** Too Many Requests — rate limited
- **500** Internal Server Error — unhandled server fault

### Response envelope
Consistent shape for all responses:
```typescript
{
  success: boolean
  data: T | null
  error: string | null
  metadata?: { total, page, limit }
}
```

## Endpoint design patterns

### Pagination
- Cursor-based for large/changing sets: `?cursor=abc&limit=20`
- Offset-based for small stable sets: `?page=1&limit=20`
- Always cap `limit` server-side (max 100)

### Filtering
- Query params: `?status=active&created_after=2024-01-01`
- Sort: `?sort=-created_at` (minus prefix = descending)

### Versioning
- URL path: `/v1/users`, `/v2/users` (easiest to deprecate)
- Never introduce breaking changes to existing version

## Security (mandatory)

- **Authentication** — every non-public endpoint checks auth first
- **Authorization** — row-level checks, not just auth-exists
- **Input validation** — Zod schema on every request body + query
- **Rate limiting** — public routes + AI/LLM routes especially
- **CORS** — whitelist, not `*`
- **Output filtering** — never leak internal IDs or PII in error messages
- **Webhook signatures** — verify signature before trusting payload

## Error handling

- Never expose stack traces to the client
- Log server-side with request ID
- Return structured error: `{ code: "INVALID_INPUT", message: "...", field: "email" }`
- HTTP status code must match error type

## Output format

```markdown
## API Design Summary

### Endpoint
`<METHOD> /path/to/resource`

### Purpose
<what it does, who uses it>

### Request
- **Auth:** <required | optional>
- **Body schema:** Zod
- **Query params:** ...

### Response
- **200:** <shape>
- **Error cases:** 400, 401, 403, 404, 422, 429, 500

### Security checks
- [ ] Auth verified
- [ ] Authorization verified (row-level)
- [ ] Input validated (Zod)
- [ ] Rate limit applied
- [ ] PII not leaked in errors

### Dependencies
- Database tables: <list>
- External services: <list>
```

## Rules

- **RESTful first.** Only use GraphQL / RPC if there's a concrete reason.
- **No breaking changes** to existing API versions. Ever.
- **Every endpoint validates input** — no "we'll add validation later".
- **Every endpoint has a test** (unit for business logic, integration for HTTP layer).
- **Document before coding.** OpenAPI spec or at least a Markdown contract.
- **Rate limit on day 1** — retrofitting is painful.
