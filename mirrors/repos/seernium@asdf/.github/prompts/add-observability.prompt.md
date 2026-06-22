---
mode: agent
description: Add structured logging, request correlation, and error tracking to a module or endpoint.
---

Invoke the `observability-engineer` agent to:
1. Audit the target module for `console.log` usage and replace with structured pino logger.
2. Add `X-Request-Id` correlation ID propagation if not present.
3. Integrate Sentry `captureException` for unhandled errors with user ID context (not PII).
4. Configure PII redaction for any sensitive fields in log output.
5. Verify zero `console.log` calls remain in production server paths.

Target module: ${input}
