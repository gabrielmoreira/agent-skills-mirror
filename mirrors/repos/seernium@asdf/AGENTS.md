# Multi-Agent Orchestration System

This repository uses **two** agentic frameworks:

1. **GitHub Copilot Enterprise** — `.github/copilot-instructions.md` + `.github/agents/*.agent.md`
2. **Claude Code** — `CLAUDE.md` + `.claude/agents/*.md`

Both frameworks share the same architecture: a pipeline of specialist agents that plan, implement, review, test, and deploy code.

---

## GitHub Copilot System

| Layer | Location | Purpose |
|---|---|---|
| Always-on | `.github/copilot-instructions.md` | Repo-wide rules injected into every prompt |
| Scoped rules | `.github/instructions/*.instructions.md` | Per-filetype conventions (`applyTo` glob) |
| Skills | `.github/skills/<name>/SKILL.md` | Reusable multi-step workflows |
| Agents | `.github/agents/*.agent.md` | Specialist personas |
| Prompts | `.github/prompts/*.prompt.md` | On-demand `/slash-commands` |
| Hooks | `.github/hooks/*.hooks.json` + `scripts/` | Guardrails |
| MCP | `.vscode/mcp.json` | External tool access |

## Claude Code System

| Layer | Location | Purpose |
|---|---|---|
| Always-on | `CLAUDE.md` | Repo-wide rules |
| Scoped rules | `.claude/rules/*.md` | Per-filetype conventions |
| Skills | `.claude/skills/<name>/SKILL.md` | Reusable multi-step workflows |
| Agents | `.claude/agents/*.md` | Specialist personas |
| Commands | `.claude/commands/*.md` | On-demand slash commands |
| Hooks | `.claude/hooks/*.hooks.json` + `scripts/` | Guardrails |
| MCP | `.claude/mcp.json` | External tool access |

## Shared Agent Roster

All agents apply to both frameworks unless noted:

| Agent | Role | Copilot File | Claude Code File |
|---|---|---|---|
| `@planner` | Architectural blueprint, zero code | `.github/agents/planner.agent.md` | `.claude/agents/planner.md` |
| `@implementer` | Core code synthesis and orchestration | `.github/agents/implementer.agent.md` | `.claude/agents/implementer.md` |
| `@frontend-ui` | React/Next.js/Tailwind specialist | `.github/agents/frontend-ui.agent.md` | `.claude/agents/frontend-ui.md` |
| `@backend-api` | Node.js/API/Server Actions specialist | `.github/agents/backend-api.agent.md` | `.claude/agents/backend-api.md` |
| `@database-architect` | Prisma schema design, migrations, index strategy | `.github/agents/database-architect.agent.md` | `.claude/agents/database-architect.md` |
| `@code-reviewer` | Quality, lint, test coverage verification | `.github/agents/code-reviewer.agent.md` | `.claude/agents/code-reviewer.md` |
| `@security-reviewer` | OWASP Top 10 vulnerability audit | `.github/agents/security-reviewer.agent.md` | `.claude/agents/security-reviewer.md` |
| `@performance-engineer` | Bundle size, query latency, Core Web Vitals | `.github/agents/performance-engineer.agent.md` | `.claude/agents/performance-engineer.md` |
| `@accessibility-auditor` | WCAG 2.1 AA compliance | `.github/agents/accessibility-auditor.agent.md` | `.claude/agents/accessibility-auditor.md` |
| `@observability-engineer` | Structured logging, distributed tracing, alerting | `.github/agents/observability-engineer.agent.md` | `.claude/agents/observability-engineer.md` |
| `@api-contract` | OpenAPI spec generation, versioning, contract testing | `.github/agents/api-contract.agent.md` | `.claude/agents/api-contract.md` |
| `@e2e-tester` | Puppeteer browser-driven E2E tests | `.github/agents/e2e-tester.agent.md` | `.claude/agents/e2e-tester.md` |
| `@local-deployment-engineer` | Docker/compose, local prod parity | `.github/agents/local-deployment-engineer.agent.md` | `.claude/agents/local-deployment-engineer.md` |
| `@cloud-deployment-engineer` | AWS ECS/Vercel deployment + CI/CD | `.github/agents/cloud-deployment-engineer.agent.md` | `.claude/agents/cloud-deployment-engineer.md` |
| `@pr-author` | PR descriptions, changelog entries, migration guides | `.github/agents/pr-author.agent.md` | `.claude/agents/pr-author.md` |

## Orchestration Flow

```
@planner → @implementer → @frontend-ui / @backend-api / @database-architect
         → @code-reviewer → @security-reviewer → @performance-engineer
         → @accessibility-auditor → @observability-engineer
         → @api-contract → @e2e-tester
         → @local-deployment-engineer → @cloud-deployment-engineer
         → @pr-author
```

For scoped single-layer work, jump directly to `@frontend-ui` or `@backend-api`.

## Tech Stack

- **Languages & Runtimes:** TypeScript (Strict), Node.js v22 (LTS)
- **Frontend:** Next.js 15 (App Router), React 19, Tailwind CSS v4
- **Data Layer:** Zod v3, Prisma ORM
- **Testing:** Vitest, RTL, Puppeteer
- **Deployment:** Docker, Docker Compose, AWS ECS, Vercel
- **Package Manager:** pnpm

## CLI Commands

| Command | Purpose |
|---|---|
| `pnpm dev` | Start dev server |
| `pnpm tsc --noEmit` | Typecheck |
| `pnpm lint` | Lint |
| `pnpm test` | Unit/component tests |
| `pnpm test:e2e:puppeteer` | E2E tests |
| `pnpm audit` | Vulnerability scan |
| `docker compose up --build` | Containerized run |