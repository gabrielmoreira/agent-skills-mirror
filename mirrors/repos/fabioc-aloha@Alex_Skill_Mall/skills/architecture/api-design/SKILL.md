---
type: skill
lifecycle: stable
inheritance: inheritable
name: api-design
description: Design APIs that developers love to use.
tier: standard
applyTo: '**/*api*,**/*design*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# API Design Skill


> Design APIs that developers love to use.

## Core Principle

A good API is intuitive, consistent, and hard to misuse. Design for the consumer, not the implementation.

## REST Fundamentals

### Resource Naming

| Good | Bad | Why |
|------|-----|-----|
| `/users` | `/getUsers` | Nouns, not verbs |
| `/users/123` | `/user?id=123` | Path params for identity |
| `/users/123/orders` | `/getUserOrders` | Hierarchical resources |
| `/search?q=term` | `/search/term` | Query params for filters |

### HTTP Methods

| Method | Purpose | Idempotent | Safe |
|--------|---------|------------|------|
| GET | Read resource | Yes | Yes |
| POST | Create resource | No | No |
| PUT | Replace resource | Yes | No |
| PATCH | Partial update | No* | No |
| DELETE | Remove resource | Yes | No |

### Status Codes

| Code | Meaning | When to Use |
|------|---------|-------------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Missing authentication |
| 403 | Forbidden | Authenticated but not allowed |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | State conflict (duplicate) |
| 429 | Too Many Requests | Rate limited |
| 500 | Internal Error | Server bug |

## Contract-First Design

1. **Define the contract** (OpenAPI/Swagger)
2. **Review with consumers** before coding
3. **Generate server stubs** from contract
4. **Implement business logic**
5. **Validate responses** against contract

```yaml
openapi: 3.1.0  # 3.1.0 aligns with JSON Schema 2020-12
info:
  title: My API
  version: 1.0.0
paths:
  /users:
    get:
      summary: List users
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserList'
```

## Versioning

| Strategy | Example | Recommendation |
|----------|---------|----------------|
| URL Path | `/v1/users` | Preferred - explicit |
| Header | `Accept: vnd.api.v1+json` | Clean but hidden |
| Query | `/users?version=1` | Avoid |

## Pagination Patterns

### Offset-Based

```json
GET /users?offset=40&limit=20
{ "data": [...], "pagination": { "total": 150 } }
```

### Cursor-Based (Preferred for large datasets)

```json
GET /users?cursor=abc123&limit=20
{ "data": [...], "next_cursor": "def456" }
```

## Error Response Design

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": [{ "field": "email", "message": "Invalid format" }],
    "request_id": "req_abc123"
  }
}
```

**Principles**:

- Machine-readable code
- Human-readable message
- Request ID for correlation
- Never expose stack traces

## Caching

### HTTP Cache Headers

| Header | Purpose |
|--------|---------|
| `Cache-Control` | Caching directives |
| `ETag` | Content fingerprint |
| `Vary` | Cache key factors |

```http
Cache-Control: public, max-age=3600
Cache-Control: private, max-age=300
Cache-Control: no-store
```

### ETag Flow

```http
GET /users/123
-> 200 OK, ETag: "v1-abc123"

GET /users/123, If-None-Match: "v1-abc123"
-> 304 Not Modified (or 200 with new ETag)
```

## Rate Limiting

### Algorithms

| Algorithm | Description |
|-----------|-------------|
| Fixed Window | X requests per minute |
| Token Bucket | Burst-friendly with refill |
| Sliding Window | Rolling time window |

### Response Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1706792400

# When exceeded
429 Too Many Requests
Retry-After: 30
```

### Rate Limit Tiers

| Tier | Limit | Use Case |
|------|-------|----------|
| Anonymous | 60/hour | Public exploration |
| Authenticated | 1000/hour | Normal usage |
| Premium | 10000/hour | Power users |

## Request/Response Design

- Use camelCase or snake_case consistently
- Timestamps in ISO 8601: `2026-02-01T14:30:00Z`
- IDs as strings (future-proof for UUIDs)
- Envelope responses: `{ "data": ..., "meta": ... }`

### Partial Responses

```
GET /users/123?fields=id,name,email
```

## Security Checklist

- [ ] Authentication on all non-public endpoints
- [ ] Authorization checked for each resource
- [ ] Rate limiting enabled
- [ ] Input validation (size limits, type checking)
- [ ] No sensitive data in URLs
- [ ] CORS configured appropriately
- [ ] Audit logging for sensitive operations

## Documentation Requirements

- **Authentication**: How to get and use tokens
- **Quick Start**: Working example in < 5 minutes
- **Reference**: Every endpoint, parameter, response
- **Errors**: All error codes and recovery steps
- **Changelog**: What changed in each version

## API Review Checklist

- [ ] Resource names are nouns, plural
- [ ] HTTP methods match semantics
- [ ] Status codes are appropriate
- [ ] Error responses are consistent
- [ ] Pagination for lists
- [ ] Versioning strategy clear
- [ ] Rate limits defined
- [ ] OpenAPI spec accurate

## Anti-Patterns

- Verbs in URLs (`/getUser`)
- Exposing internal IDs (auto-increment)
- Inconsistent naming conventions
- No versioning strategy
- Missing rate limits
- Exposing stack traces in errors
- Breaking changes without version bump
