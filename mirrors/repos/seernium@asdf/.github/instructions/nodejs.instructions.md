---
applyTo: "src/server/**/*.ts,src/app/api/**/*.ts,scripts/**/*.ts"
description: "Node.js backend, API, and server-side conventions"
---

# Node.js / Backend Conventions

- Use native `fetch` (Node 18+) — no `axios` unless interceptors/cancellation are genuinely needed.
- All I/O (DB, network, fs) is `async/await`; no callback-style APIs, no unhandled promise rejections.
- Wrap route/handler logic in a try/catch that returns a structured error shape: `{ error: { code, message } }`.
- Input validation with `zod` at every boundary (API route body/query/params, queue consumers, CLI args) — never trust `request.json()` output directly.
- Database access goes through a single client/ORM instance (e.g. Prisma/Drizzle) exported from `src/server/db.ts` — never instantiate new clients ad hoc.
- Logging: use a structured logger (`pino` or similar), never bare `console.log` in server code (CLI scripts are the exception).
- Secrets/config: read via a typed `src/server/env.ts` that validates `process.env` with `zod` at startup — fail fast on missing vars.
- Rate-limit and auth-check any public-facing route handler; document the auth model in a comment at the top of the file.
- Background/long-running work goes through a queue (or `after()` in Next.js) — never block a request handler on slow work.
