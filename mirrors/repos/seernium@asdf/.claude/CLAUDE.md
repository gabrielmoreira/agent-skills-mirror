# Claude Code Multi-Agent Orchestration System

This repository uses Claude Code's agentic framework with a multi-persona architecture. See `.claude/rules/` for scoped instructions and `.claude/agents/` for specialist personas.

## Tech Stack
- **Languages & Runtimes:** TypeScript (Strict Mode), Node.js v22 (LTS)
- **Frontend:** Next.js 15 (App Router, Server Components First), React 19, Tailwind CSS v4
- **Data Layer & Validation:** Zod v3, Prisma ORM
- **Testing:** Vitest, React Testing Library, Puppeteer
- **Deployment:** Docker, Docker Compose, AWS ECS, Vercel
- **Package Manager:** pnpm

## Fundamental Directives
1. **No Hallucinated Imports** — Verify file existence and exports before generating import lines.
2. **Strict TypeScript** — No `any`, no `//@ts-ignore`. Use explicit interfaces or generic assertions.
3. **Zod Validation** — Every API Route Handler, Server Action, or URL search-param must be validated via Zod.
4. **No Placeholders** — No `// TODO: implement later`. Emit full, concrete implementation blocks.
5. **Security Isolation** — API keys and secrets bound to `process.env` only. No hardcoded credentials. Use `src/server/env.ts` (see `env-validator` skill).
6. **Error Resiliency** — Wrap async operations in try/catch with graceful fallback logic. Never leak internal error details to clients.
7. **Runtime Env Validation** — All required environment variables must be validated at startup using the `env-validator` skill. Never access `process.env` directly in business logic.
8. **Observability Required** — All server-side code paths must use the `structured-logger` skill. No `console.log` in production code paths.
9. **Clean Code & SOLID** — Adhere strictly to clean-code principles (KISS, YAGNI, max 40-line functions, SRP split files) specified in `clean-code.md` rules.
10. **TypeScript Wizardry** — Follow nominal/branded typing for domain primitives and explicit return types specified in `typescript-wizardry.md` rules.

## Agent Roster
| Agent | Role |
|---|---|
| `@planner` | Architectural blueprint, zero code |
| `@implementer` | Core code synthesis and orchestration |
| `@frontend-ui` | React/Next.js/Tailwind specialist |
| `@backend-api` | Node.js/API/Server Actions specialist |
| `@database-architect` | Prisma schema design, migrations, index strategy |
| `@code-reviewer` | Quality, lint, test coverage verification |
| `@security-reviewer` | OWASP Top 10 vulnerability audit |
| `@performance-engineer` | Bundle size, query latency, Core Web Vitals |
| `@accessibility-auditor` | WCAG 2.1 AA compliance |
| `@observability-engineer` | Structured logging, distributed tracing, alerting |
| `@api-contract` | OpenAPI spec generation, versioning, contract testing |
| `@e2e-tester` | Puppeteer browser-driven E2E tests |
| `@local-deployment-engineer` | Docker/compose, local prod parity |
| `@cloud-deployment-engineer` | AWS ECS/Vercel deployment + CI/CD |
| `@pr-author` | PR descriptions, changelog entries, migration guides |

## Orchestration Flow
`@planner` → `@implementer` → (specialists as needed) → `@code-reviewer` → `@security-reviewer` → `@performance-engineer` → `@accessibility-auditor` → `@e2e-tester` → `@local-deployment-engineer` → `@cloud-deployment-engineer`

## CLI Commands
- `pnpm dev` — Start dev server
- `pnpm tsc --noEmit` — Typecheck
- `pnpm lint` — Lint
- `pnpm test` — Unit/component tests
- `pnpm test:e2e:puppeteer` — E2E tests
- `pnpm audit` — Vulnerability scan
- `docker compose up --build` — Containerized run

## System Layers
| Layer | Location | Purpose |
|---|---|---|
| Root instructions | `CLAUDE.md` | Always-on repo-wide rules |
| Scoped rules | `.claude/rules/*.md` | Per-filetype conventions |
| Skills | `.claude/skills/<name>/SKILL.md` | Reusable multi-step workflows |
| Agents | `.claude/agents/*.md` | Specialist personas |
| Commands | `.claude/commands/*.md` | Slash commands |
| Hooks | `.claude/hooks/*.hooks.json` | Guardrails |
| MCP | `.claude/mcp.json` | External tool access |