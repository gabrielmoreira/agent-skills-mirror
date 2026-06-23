# Repository-wide Copilot Instructions

This file is ALWAYS loaded by GitHub Copilot for every chat/agent request in this repo.
Keep it short and high-signal — put framework-specific detail in `.github/instructions/*.instructions.md` instead.

## Stack
- TypeScript (strict mode) across the entire codebase — no `any`, no implicit `any`
- Next.js (App Router) for the web app — `src/app/**`
- React Server Components by default; `"use client"` only when interactivity/hooks are required
- Tailwind CSS for all styling — no inline `style=`, no CSS-in-JS
- Node.js for backend services / API routes — `src/server/**`, `src/app/api/**`
- Package manager: pnpm. Always use `pnpm`, never `npm` or `yarn` in generated commands.

## Non-negotiable rules
1. Never introduce a new dependency without first checking `package.json` for an existing one that already solves the problem.
2. Every exported function/component must have an explicit return type.
3. Server Actions and API routes must validate input with `zod` before use.
4. No secrets, API keys, or tokens in code — use `process.env` and document required vars in `.env.example`.
5. All new UI must be responsive (mobile-first) and pass basic a11y (semantic HTML, labelled inputs, focus states).
6. Tests are required for new business logic (`*.test.ts`) and new components (`*.test.tsx`).
7. Adhere to Clean Code/SOLID principles (KISS, YAGNI, early returns, max 40-line functions) specified in `clean-code.instructions.md`.
8. Enforce nominal/branded typing and explicit function returns as specified in `typescript-wizardry.instructions.md`.

## Where to look first
- Coding conventions per file type → `.github/instructions/`
- Reusable multi-step workflows → `.github/skills/`
- Specialized personas (refactor, review, test) → `.github/agents/`
- One-off slash commands → `.github/prompts/`
- External tool/data access → `.vscode/mcp.json`
- Deterministic guardrails (lint/secret checks before commits) → `.github/hooks/`
