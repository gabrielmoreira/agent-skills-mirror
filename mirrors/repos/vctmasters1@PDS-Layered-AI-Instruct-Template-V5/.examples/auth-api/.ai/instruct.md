# auth-api — Module AI Instructions (Example)

**Scope**: Authoritative for everything inside `.examples/auth-api/`
**Last Updated**: 2026-05-25

> Example module. See [`.examples/README.md`](../../README.md) for context.
> In a real project this file would live at `auth-api/.ai/instruct.md` (no `.examples/` prefix).

---

## Contents

| Section | What's here |
|---|-------------|
| [Module Overview](#module-overview) | Purpose, entry point, dependencies |
| [Directory Structure](#directory-structure) | Internal layering |
| [Module-Specific Rules](#module-specific-rules) | The rules the AI must follow inside this module |
| [Security Rules](#security-rules) | Auth-specific hard rules |
| [Testing Rules](#testing-rules) | What must be tested and how |
| [Global Rules Reference](#global-rules-reference) | Cross-references — never restate |

---

## Module Overview

`auth-api` is the **authentication and session service**. It owns user signup, password login, password reset, JWT issuance, and session revocation. It is the only module allowed to read or write the `users`, `sessions`, and `password_resets` tables.

- **Entry point**: `src/index.ts` → `createServer()`
- **Transport**: HTTP/JSON over Express, all routes mounted under `/v1/auth/*`
- **Token format**: HS256 JWT, 15-minute access + 30-day refresh (rotating)
- **Dependencies on other modules**: [`data-layer/`](../../data-layer/) for entity definitions and the repository base class
- **External dependencies**: PostgreSQL, SendGrid (password-reset emails), Redis (session blacklist)

---

## Directory Structure

```
auth-api/
├── .ai/instruct.md             ← this file
├── .dev-docs/index.md
├── .env.example
├── README.md                    ← reading order for the worked code
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts                ← server bootstrap; nothing else
│   ├── routes/                 ← Express routers only — thin HTTP adapters
│   │   ├── signup.route.ts
│   │   ├── login.route.ts
│   │   └── reset-password.route.ts
│   ├── services/               ← business logic; routes call services
│   │   ├── auth.service.ts
│   │   └── token.service.ts        ← only place that calls jwt.sign / jwt.verify
│   ├── repositories/           ← the only place that touches the DB
│   │   ├── user.repository.ts
│   │   └── session.repository.ts
│   ├── lib/                    ← framework-agnostic helpers (hash, errors, response, logger, timing)
│   └── schemas/                ← Zod request/response schemas
├── scripts/
│   └── check-layering.mjs       ← CI gate — fails if routes import repositories
└── test/
    ├── unit/                   ← services + lib (repos mocked)
    └── integration/            ← routes against a real Postgres test container
```

---

## Module-Specific Rules

### Layering

1. **Routes never call the database directly.** Routes call services; services call repositories; repositories call the ORM. Enforced by [`scripts/check-layering.mjs`](../scripts/check-layering.mjs) (`npm run lint:layering`) as a CI gate.
2. **Repositories never throw HTTP errors.** They throw domain errors (`UserNotFoundError`, `EmailTakenError`) defined in `src/lib/errors.ts`. Services translate them to HTTP at the boundary.
3. **No business logic in routes.** A route handler is at most: validate input with Zod → call one service method → format response envelope → send.
4. **All responses use the `{ data, error, meta }` envelope** from `src/lib/response.ts`. No raw entity dumps.

### Versioning

- Every public route lives under `/v1/`. Breaking changes ship as `/v2/` while `/v1/` continues to work. See [Versioning](../../../.ai/conventions.md#versioning).

### Logging

- Use the shared `logger` from `src/lib/logger.ts`. **Never** `console.log` outside of `src/index.ts` bootstrap.
- Logs are structured JSON. **Never** log: password fields, raw JWTs, refresh tokens, reset codes, or full request bodies on auth routes.

---

## Security Rules

These are non-negotiable. The AI must reject any code change that violates them and propose a conforming alternative.

1. **Passwords**: hash with `argon2id` (parameters in `src/lib/hash.ts`). Never store, log, or return a password — hashed or otherwise.
2. **JWT secret**: read from `process.env.JWT_SECRET` at startup, fail-fast if missing. Never inline a secret, never accept it from a request header.
3. **Token verification**: always verify both signature **and** `exp`/`nbf`. Helper `verifyAccessToken()` is the only allowed entry point — do not call `jwt.verify` directly elsewhere.
4. **Refresh tokens**: rotate on every use; the old token is blacklisted in Redis with TTL = remaining lifetime. No exceptions.
5. **Rate limiting**: `/login` and `/reset-password` routes wear the `authRateLimit` middleware. Adding a new auth route without it is a blocker.
6. **No PII in URLs or query strings.** Email, phone, and user IDs go in the body or JWT claims, never the path.
7. **Timing-safe comparisons** for any secret/token comparison — `crypto.timingSafeEqual`, never `===`.

> **→ [Never Commit Credentials](../../../.ai/credentials.md#never-commit-credentials)** — all secrets via env vars.

---

## Testing Rules

- Every service method has unit tests with the repository mocked.
- Every route has at least one integration test that hits a real Postgres (testcontainers) and a real Redis.
- A new auth route without an integration test is incomplete and must not be merged.
- Tests **never** use production-shaped secrets. The test JWT secret is hard-coded in `test/fixtures/secrets.ts` and is `"test-only-do-not-use"`.

---

## Global Rules Reference

> **→ [No-Duplication Rule](../../../.ai/conventions.md#no-duplication-rule)** — instructions live in one place.
> **→ [Never Delete Rule](../../../.ai/maintenance.md#never-delete-rule)** — archive instead of delete.
> **→ [Never Reset Databases](../../../.ai/maintenance.md#never-reset-databases)** — auth tables especially require confirmation.
> **→ [.env File Convention](../../../.ai/credentials.md#env-file-convention)** — per-module flat `.env.example`.
