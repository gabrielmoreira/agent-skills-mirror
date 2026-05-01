# My SaaS Landing Page — Claude Code Instructions

## Project overview

A landing page with pricing, authentication, and Stripe payments.

## Stack

| Layer      | Choice                           |
|------------|----------------------------------|
| Framework  | Next.js 15 (App Router)          |
| Styling    | Tailwind CSS v4 + shadcn/ui      |
| DB + Auth  | Supabase                         |
| Payments   | Stripe                           |
| Validation | Zod                              |
| Deploy     | Vercel                           |

## Rules

- **Immutable patterns.** Use spread operators, `.map/.filter/.reduce`. No direct mutation.
- **File size.** 200–400 lines ideal, 800 absolute max.
- **Function size.** Max 50 lines, max 4 levels of nesting.
- **TDD.** Required for auth, payments, and anything security-sensitive.
- **Validation.** Zod at every boundary — API inputs, LLM outputs, file uploads.
- **Secrets.** Always via `process.env`, never in code.

## Workflow

Features follow this agent chain:

```
USER REQUEST
    ↓
planner    → produces implementation plan
    ↓
ui-agent   → produces component brief
    ↓
builder    → writes tests + code (TDD)
    ↓
reviewer   → quality + security check
    ↓
(if CRITICAL found → loop back to builder)
    ↓
COMMIT
```

## Agents

Defined in `.claude/agents/`:

| Agent     | Role                              | Tools                          |
|-----------|-----------------------------------|--------------------------------|
| planner   | Planning + architecture           | Read, Grep, Glob               |
| ui-agent  | Design + component decisions      | Read, Grep, Glob               |
| builder   | Code implementation (TDD)         | Read, Write, Edit, Bash, Grep  |
| reviewer  | Code quality + security           | Read, Grep, Glob, Bash         |

**Note:** No agent has `Task` tool — subagents cannot spawn other subagents. Main Claude orchestrates.

## Skills

Defined in `.claude/skills/`. See `.claude/skills/README.md` for source attribution.

| Skill             | Used by    | Source                                           |
|-------------------|------------|--------------------------------------------------|
| `plan`            | planner    | community (alirezarezvani/claude-skills)         |
| `ui-ux-pro-max`   | ui-agent   | nextlevelbuilder/ui-ux-pro-max-skill             |
| `api-design`      | builder    | wshobson/agents (backend-development plugin)     |
| `code-review`     | reviewer   | anthropics/claude-code (official)                |
| `security-review` | reviewer   | anthropics/claude-code-security-review           |
