---
mode: agent
description: Generate an OpenAPI 3.1 specification from existing route handlers and Zod schemas.
---

Invoke the `api-contract` agent to:
1. Scan all route handlers in `src/app/api/**` and Server Actions.
2. Extract Zod input/output schemas and map to OpenAPI 3.1 path operations.
3. Write or update `docs/api/openapi.yaml` with reusable `components/schemas`.
4. Document security schemes on all protected endpoints.
5. Classify changes vs. the existing spec (if any) as breaking or non-breaking.
6. If breaking: recommend versioning strategy and write a migration guide.

Scope: ${input:all routes}
