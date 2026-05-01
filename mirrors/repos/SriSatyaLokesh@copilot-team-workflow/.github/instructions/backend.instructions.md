---
applyTo: "src/api/**,src/services/**,src/repositories/**,src/db/**,src/middleware/**"
---
# Backend Development Standards

## Architecture Layers
Follow the repository pattern strictly:
- **Routes** (`src/api/`): HTTP handling only — validate, call service, return response
- **Services** (`src/services/`): Business logic, orchestration, no DB calls
- **Repositories** (`src/repositories/`): All database interactions
- Never query the DB directly from routes or services

## Input Validation
- All route handler inputs must be validated with `zod`
- Define schemas in `src/api/[resource]/[resource].schema.ts`
- Return `400` for validation errors with field-level error messages

## Error Handling
- Use structured error responses: `{ error: string, code: string, details?: object }`
- Never expose raw DB errors, stack traces, or internal details to clients
- Use `try/catch` in route handlers; let unhandled errors propagate to global handler
- Log all errors with: `logger.error({ error, context }, 'message')`

## Authentication & Authorization
- All non-public endpoints must use `requireAuth` middleware
- Check permissions in the service layer, not just middleware
- Role-based access: check `user.role` in service, not route

## Logging
- Use structured logging (not `console.log`)
- Log format: `logger.info({ userId, action, context }, 'message')`
- Never log sensitive data (passwords, tokens, PII)

## Performance
- Add database indexes for all foreign keys and commonly filtered fields
- Use pagination for all list endpoints (default limit: 20, max: 100)
- Cache expensive queries with Redis; invalidate on mutation

## API Conventions
- RESTful naming: `/api/resources` (plural, noun, lowercase)
- Use HTTP verbs correctly: GET (read), POST (create), PUT/PATCH (update), DELETE
- Always include `Content-Type: application/json`
- Return `201` for creates, `200` for updates, `204` for deletes
