---
name: error-handling-contracts
description: Design consistent backend and API error handling contracts. Use when Codex is asked to define error response shapes, status codes, validation errors, retry behavior, logging, observability, client-safe messages, or failure semantics.
license: MIT
---

# Error Handling Contracts

## Core Workflow

1. Identify clients, failure modes, transport, user-facing surfaces, and logging
   or observability needs.
2. Define an error envelope with code, message, details, correlation ID, retry
   guidance, and documentation link where useful.
3. Map domain failures to status codes or exception types.
4. Separate client-safe messages from internal diagnostics.
5. Specify retryability, idempotency, rate-limit behavior, and partial failure
   handling.
6. Add tests and examples for expected error cases.

## Safety Rules

- Do not expose stack traces, secrets, SQL, internal hosts, or sensitive user
  data in client-facing errors.
- Do not use errors to hide authorization decisions when explicit denial is
  required by product or compliance needs.
- Escalate error contracts for payments, auth, customer data, or public APIs.

## Deliverable Shape

For error contracts, provide:

- Error envelope
- Status code or exception mapping
- Validation error format
- Retry and idempotency guidance
- Logging and correlation guidance
- Client-safe versus internal fields
- Examples
- Test cases

## References

- Read `references/error-handling-contracts-checklist.md` when designing or
  reviewing backend error handling.
