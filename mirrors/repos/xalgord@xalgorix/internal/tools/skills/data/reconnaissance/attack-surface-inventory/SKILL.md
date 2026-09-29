---
name: attack-surface-inventory
description: Structured normalization of discovered attack surface into the Endpoint Inventory note for downstream planning
---

# Attack Surface Inventory

## When to Use
After crawling, content discovery, JS analysis, and API discovery, normalize all findings into a structured inventory that the planner and specialist lanes can consume.

## Format

Save an `add_note` with key "Endpoint Inventory" using this structure:

```
GET / - main page
GET /login - login form
POST /login - form action (params: username,password)
GET /api/users - API endpoint (params: ?id, ?page)
GET /search - search (params: ?q)
POST /api/search - API search (JSON body: query,limit)
GET /admin - admin panel (requires auth)
GET /static/app.js - JS bundle
GET /openapi.yaml - API spec
```

## Normalization Rules
- One route per line: `METHOD path - description (params: ...)`
- Strip query values, keep parameter names: `?id=123` becomes `(params: id)`
- Deduplicate trailing-slash variants: `/api/users/` and `/api/users` are one entry
- Mark auth requirement: `(requires auth)`, `(admin only)`
- Mark source: `(source: crawl)`, `(source: openapi)`, `(source: js)`, `(source: dirbust)`
- Include HTTP method when known (default GET)
- Include content type when useful: `(JSON)`, `(XML)`, `(HTML)`

## Handoff
The Endpoint Inventory feeds:
1. `AutoPlan` — builds class tasks listing every discovered endpoint
2. `CoverageGaps` — per-endpoint × class gap detection
3. Specialist lanes — partition the surface

## Common Misses
- Only listing GET routes (missing POST/PUT/DELETE)
- Not including path parameters (/users/{id})
- Missing WebSocket endpoints
- Forgetting to note which routes require authentication
