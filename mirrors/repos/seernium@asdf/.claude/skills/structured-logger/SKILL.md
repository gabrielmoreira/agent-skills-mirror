# Skill: structured-logger

Provides a pino-based structured logging pattern with request correlation IDs and PII redaction.

## When to use
- Adding or upgrading logging in any server-side module
- Setting up observability for a new service
- Replacing `console.log` calls in production code

## Files
- `logger.template.ts` — Pino-based structured logger with correlation + redaction

## Setup
1. Install: `pnpm add pino pino-pretty`
2. Place at `src/server/logger.ts`
3. Use `AsyncLocalStorage` to propagate the request correlation ID through the request lifecycle

## Conventions
- Never log: passwords, full email addresses (log only domain part), credit card numbers, SSNs, auth tokens
- Log levels: `debug` (dev only), `info` (key business events), `warn` (recoverable issues), `error` (exceptions + SLO breaches)
- Every log line in a request context must include `requestId`
