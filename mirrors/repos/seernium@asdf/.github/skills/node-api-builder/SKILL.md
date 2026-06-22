---
name: node-api-builder
description: Build a new Node.js API endpoint (Next.js Route Handler or standalone Node/Express service) with validation, error handling, and structured responses following this repo's conventions. Use when asked to "add an endpoint", "create an API route", or "build a backend handler".
---

# Node.js API Builder Skill

## Process

1. **Decide the host**: Next.js Route Handler (`src/app/api/<resource>/route.ts`) for app-coupled endpoints, or a standalone service file under `src/server/routes/` if this repo has a separate Node/Express backend — check `src/server/` for an existing pattern first.
2. **Define the schema first** — write the `zod` schema for the request body/query/params before writing the handler logic.
3. **Use [route-handler-template.ts](./route-handler-template.ts)** as the starting structure.
4. **Status codes**: `200` success, `201` created, `400` validation error, `401` unauthenticated, `403` unauthorized, `404` not found, `409` conflict, `500` unexpected — never return `200` with an error payload.
5. **Auth check** happens first in the handler, before any validation or DB call, to fail fast and avoid unnecessary work.
6. **Errors**: catch and return the structured shape `{ error: { code: string; message: string } }`; log the original error server-side with the structured logger, don't leak internals to the client.
7. **Add a test** hitting the handler directly (or via `supertest`/integration test) covering: success case, validation failure, auth failure.

## Checklist
- [ ] `zod` schema validates all external input
- [ ] Correct HTTP status codes used
- [ ] Auth checked before business logic
- [ ] Errors logged server-side, sanitized client-side
- [ ] Test covers success + at least one failure path
