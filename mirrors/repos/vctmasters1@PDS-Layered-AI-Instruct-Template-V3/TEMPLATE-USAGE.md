# TEMPLATE-USAGE — How to Adapt This Template

This guide walks you through customizing the **Depth-Priority Hierarchical-Instruct V1** template for a new project.

> **Fastest path: run `/hip-onboard` in Copilot Chat.** It's an interactive wizard that walks through Steps 1–6 below, asks focused questions, detects/infers defaults where safe, fills every `[PLACEHOLDER]` it can (including `.hi/dev-specs.md`), and asks you to confirm/edit inferred values. The manual steps below remain available if you prefer to drive it yourself or need to redo one section.
>
> **Faster than that: run the one-shot installer.** From a fresh clone, run `bash setup.sh` (macOS/Linux/WSL/Git Bash) or `pwsh setup.ps1` (Windows). It installs the git hooks, scaffolds `.env`, and runs the validator. Then drive `/hip-onboard` in Copilot Chat for the placeholder pass.

---

## Contents

| Section | What's here |
|---|-------------|
| [What You Get](#what-you-get) | What the template provides out of the box |
| [Step 1 — Project Identity](#step-1--project-identity) | Replace all placeholders |
| [Step 2 — Add Your Modules](#step-2--add-your-modules) | Scaffold per-module Hierarchical-Instructs |
| [Step 3 — Rebuild the Index](#step-3--rebuild-the-index) | Sync `.hi/index.md` |
| [Step 4 — Set Up Git Hooks](#step-4--set-up-git-hooks) | Install pre-commit safety checks |
| [Step 5 — Configure MCP](#step-5--configure-mcp) | Optional: extend AI with MCP servers |
| [Step 6 — Add Environment Variables](#step-6--add-environment-variables) | Fill in .env.example |
| [Ongoing Maintenance](#ongoing-maintenance) | How to keep the system healthy |
| [Scaling Up](#scaling-up) | How the instruction system grows with your project |
| [Companion Resources](#companion-resources) | Awesome-Copilot, Cursor compat, stack examples |
| [Feature Reference](#feature-reference) | All system components at a glance |

---

## What You Get

| Component | What it does |
|-----------|-------------|
| `.github/copilot-instructions.md` | META file — teaches Copilot how the hierarchy works |
| `.hi/dev-specs.md` | Template field sheet for platform/stack facts (filled or confirmed during onboarding) |
| `.hi/prompts/` | Slash commands — see [`.hi/index.md` → Meta & System](.hi/index.md#meta--system) for the canonical list |
| `.hi/agents/hia-explorer.agent.md` | Read-only exploration agent |
| `.hi/skills/project-navigation/SKILL.md` | Navigation skill for finding instruction sections |
| `.hi/hooks/` | Pre-commit credential safety check + installer |
| `.hi/conventions.md` | Naming, TOC, cross-reference, no-duplication rules |
| `.hi/maintenance.md` | Never-delete, archive patterns, never-reset-db rules |
| `.hi/credentials.md` | Credential warehousing, .gitignore, AI behavior |
| `.hi/index.md` | Master index — every section in every instruction file |
| `.hi/instruct.md` | Root-level project authority file |
| `.hi/example-module/` | Bare scaffold for a new module |
| `.hi/examples/` | Filled-in showcase modules (`auth-api`, `data-layer`, `ui-component`) with before/after AI behavior |
| `.cursor/rules/project.mdc` | Cursor compatibility — pointer to the `.hi/` hierarchy |
| `setup.sh` / `setup.ps1` | One-shot installer: git hooks + `.env` scaffold + validator |
| `.gitignore` | Credentials, deps, builds, OS artifacts |
| `.env.example` | Root environment variable template (flat layout) |
| `.vscode/mcp.json` | MCP server configuration template |
| `.vscode/settings.json` | Search exclusions for archive dirs |
| `AGENTS.md` | Discovery anchor for non-Copilot AI agents (Codex, Claude Code, Aider, etc.) |
| `CHANGELOG.md` | Template changelog — replace with your project changelog after adoption |
| `LICENSE` | Proprietary license — PipeDreamSystemsLLC, all rights reserved. Commercial use requires a signed agreement. |

---

## Step 1 — Project Identity

Replace every `[PLACEHOLDER]` in these files:

### `.hi/dev-specs.md`
- `/hip-onboard` pre-checks inferred values first (OS/shell/editor/language/framework/package manager), then asks you to confirm or edit
- Check all boxes matching your **development OS** and **target platform** — this prevents wrong-platform assumptions from the AI
- Check applicable frameworks, package manager, and infrastructure
- Fill in freeform fields (OS version, language version, distro, etc.)
- Tip: dev platform ≠ target platform is common (e.g., Windows dev → Linux server)

### `.hi/instruct.md` (root)
- `[PROJECT_NAME]` → your project name
- `[one-sentence description]` → what it does
- `[Tech stack]` rows → your actual stack
- Architecture diagram → your actual structure
- Key Directories table → your actual modules

### `README.md`
- `[PROJECT_NAME]` → your project name
- `[One-sentence description]` → what it does
- Quick Start commands → your actual commands
- Project Structure diagram → your actual structure

### `.env.example`
- Edit the root [`.env.example`](.env.example) — add/remove variable blocks to match your actual config needs
- Add additional environment-specific templates as needed: `.env.staging.example`, `.env.production.example` (committed; the real `.env.staging`, `.env.production` are gitignored)

---

## Step 2 — Add Your Modules

For each top-level directory in your project, create a `.hi/instruct.md`:

### Minimum viable module `.hi/instruct.md`

```markdown
# [module-name] — Module AI Instructions

**Scope**: Authoritative for everything inside `[module-name]/`
**Last Updated**: [DATE]

> Deeper than root `.hi/instruct.md` — authoritative when working in this directory.

## Module Overview
[What this module does]

## Module-Specific Rules
- [Rule 1]
- [Rule 2]

## Global Rules Reference
> **→ [Never Delete Rule](.hi/maintenance.md#never-delete-rule)** — archive instead of delete.
> **→ [Never Commit Credentials](.hi/credentials.md#never-commit-credentials)** — use env vars.
```

### Add a `.dev-docs/index.md` alongside it

```markdown
# .dev-docs Index — [module-name]

## Active Files
| File | Description | Last Updated |
|------|-------------|----------|

## Archived (`.archive/`)
| File | Why Archived | Date |
|------|-------------|------|
```

### Update the root `.hi/instruct.md` Key Directories table

Add a row for your new module in [`.hi/instruct.md` → Key Directories](.hi/instruct.md#key-directories).

### Realistic example (what a filled-in module looks like)

The shipped [`.hi/example-module/.hi/instruct.md`](.hi/example-module/.hi/instruct.md) is a placeholder scaffold. A filled-in module for, say, a Node.js API server would look more like:

```markdown
# api-server — Module AI Instructions

**Scope**: Authoritative for everything inside `api-server/`
**Last Updated**: 2026-05-25

## Module Overview
`api-server` is the public HTTP API. It exposes REST endpoints under `/v1/*`, backed by PostgreSQL via TypeORM.

**Entry point**: `src/index.ts`
**Dependencies on other modules**: `shared-entities/` (TypeORM entities)
**External dependencies**: PostgreSQL, Stripe, SendGrid

## Module-Specific Rules
- All database access goes through the repository layer in `src/repositories/` — controllers never call TypeORM directly
- All responses use the `{ data, error, meta }` envelope defined in `src/lib/response.ts`
- New endpoints must be versioned under `/v1/` or later — never unversioned
- External API calls must go through the service layer in `src/services/`, never directly from route handlers

## Global Rules Reference
> **→ [Never Commit Credentials](.hi/credentials.md#never-commit-credentials)** — all secrets via env vars.
> **→ [Never Reset Databases](.hi/maintenance.md#never-reset-databases)** — confirmation required.
```

Keep module rules **specific to that module**. Generic programming principles belong in `.hi/conventions.md`, not here.

---

## Step 3 — Rebuild the Index

After adding or changing any `.hi/instruct.md`, run:

```
/hip-update-index
```

This scans all instruction files and regenerates `.hi/index.md`.

Alternatively, update `.hi/index.md` manually by adding rows to the appropriate section group.

---

## Step 4 — Set Up Git Hooks

The pre-commit hook blocks `.env` files from being committed and warns on credential patterns.

```bash
bash .hi/hooks/install-hooks.sh
```

Run this on every developer machine after cloning. The hook only applies to that local repo clone.

To make the credential scan a **hard block** (fail the commit instead of warn), edit [.hi/hooks/pre-commit](.hi/hooks/pre-commit) — the hook is sourced live via `core.hooksPath`, so the file edits in place:

```sh
# Change this line near the end:
exit 0    # warn only
# to:
exit 1    # hard block
```

---

## Step 5 — Configure MCP

MCP servers extend what Copilot can do — database queries, GitHub access, web search, etc.

Edit `.vscode/mcp.json` and uncomment the servers you want. Each server requires:
1. The MCP server package to be installed (`npx -y` handles this automatically for npm packages)
2. Any required API keys or connection strings added to `.env` (not `.vscode/mcp.json`)

Reload VS Code after changing `mcp.json` (`Ctrl+Shift+P` → `Developer: Reload Window`).

### Recommended servers for most projects

| Server | What it adds | Package |
|--------|-------------|---------|
| `filesystem` | AI can read/write workspace files | `@modelcontextprotocol/server-filesystem` |
| `github` | AI can read issues, PRs, commits | `@modelcontextprotocol/server-github` |
| `postgres` | AI can run read-only SQL queries | `@modelcontextprotocol/server-postgres` |

---

## Step 6 — Add Environment Variables

1. Edit `.env.example` — add every key your project needs (no real values)
2. Copy to `.env` and fill in real values: `cp .env.example .env`
3. Verify `.env` is gitignored: `git check-ignore -v .env`

Each module that has its own runtime config gets its **own** flat `.env.example` (committed) and `.env` (gitignored) at its directory root — not a `.env/` subdirectory. See [.env File Convention](.hi/credentials.md#env-file-convention).

---

## Ongoing Maintenance

### When you add a module
1. Create `[module]/.hi/instruct.md` (from the template above)
2. Create `[module]/.dev-docs/index.md`
3. Add the module to root [`.hi/instruct.md` → Key Directories](.hi/instruct.md#key-directories)
4. Run `/hip-update-index`

### When you change architecture
1. Update the affected `.hi/instruct.md` in the same change
2. Update cross-references if section names changed
3. Run `/hip-update-index`

### When you archive a module or file
1. Run `/hip-archive` or follow [Archive Patterns](.hi/maintenance.md#archive-patterns)
2. If the module's `.hi/instruct.md` stays in place, add a deprecation banner (see [Stale Instruction Files](.hi/maintenance.md#stale-instruction-files))
3. Run `/hip-update-index`

### When you add environment variables
1. Add the key to root `.env.example` with a placeholder and comment
2. If module-specific, add it to the module's `.env.example` (at the module root, flat — not in a `.env/` subdirectory)

---

## Companion Resources

This template focuses on **structure**. Pair it with these community libraries when you need ready-made building blocks.

### Awesome-Copilot (recommended)

[github/awesome-copilot](https://github.com/github/awesome-copilot) is a curated catalog of 200+ Copilot instructions, prompts, agents, and skills. Most of them drop straight into this template's `.github/` directories without conflict:

| Awesome-Copilot artifact | Drop into | Notes |
|--------------------------|-----------|-------|
| `*.instructions.md` files | `.github/instructions/` (create on first use) | Per-language style guides. They layer **alongside** — not on top of — this template's depth-priority rules. |
| `*.prompt.md` files | `.hi/prompts/` | If the file name collides with one of this template's `/hip-*` commands, rename the imported one — don't overwrite. |
| `*.agent.md` files | `.hi/agents/` | Compose freely with `hia-explorer.agent.md`. |
| `SKILL.md` files | `.hi/skills/<skill>/SKILL.md` | Keep one skill per subdirectory. |

**Rule of thumb**: pull individual files you actually need; don't vendor the whole catalog. Re-run `/hip-update-index` after adding files so they show up in [.hi/index.md](.hi/index.md).

### Cursor users

The shipped [`.cursor/rules/project.mdc`](.cursor/rules/project.mdc) points Cursor at the `.hi/` hierarchy. Do **not** duplicate rules into `.cursor/rules/` — Cursor's MDC files are pointers only. The canonical rules remain in `.hi/`.

### Aider users

Add this to `.aider.conf.yml` so Aider reads the layered rules:

```yaml
read:
  - .hi/instruct.md
  - .hi/conventions.md
  - .hi/maintenance.md
  - .hi/credentials.md
```

When working in a module, also pass `--read [module]/.hi/instruct.md`.

### Stack-specific starting points

For copy-paste **Code Organization** rules tuned to common stacks, see [`.hi/stack-examples/`](.hi/stack-examples/):

- [TypeScript + React + Vite](.hi/stack-examples/typescript-react.md)
- [Python + FastAPI](.hi/stack-examples/python-fastapi.md)
- [Embedded C / C++](.hi/stack-examples/embedded-c.md)

These are reference snippets, not authoritative — paste what fits into a real `.hi/instruct.md`.

### Filled-in module examples

See [`.hi/examples/`](.hi/examples/) for three realistic module-level `.hi/instruct.md` files with **before/after AI behavior** writeups:

- [`auth-api`](.hi/examples/auth-api/) — Express + JWT + Postgres backend service.
- [`data-layer`](.hi/examples/data-layer/) — TypeORM repository / migration discipline.
- [`ui-component`](.hi/examples/ui-component/) — React + Tailwind component library.

---

## Feature Reference

The authoritative inventory of every slash command, custom agent, and skill lives in [.hi/index.md](.hi/index.md#meta--system) under **Meta & System**. Do not maintain a parallel copy here — the index is rebuilt by `/hip-update-index` and stays in sync.

### Archive Patterns Quick Reference

| Pattern | Use for |
|---------|---------|
| `<parent>/.archive/<name>` | Any file or directory — archived into the `.archive/` of its own parent folder |
| `<parent>/.archive/YYYYMMDD/<name>` | Point-in-time snapshot of a subsystem |
| `.dev-docs/.archive/` | Stale dev documentation |

Use the tool — `python .hi/engine/archive.py <path>` — rather than computing the path by hand.

### Validation

Run the bundled drift check from the project root:

```pwsh
pwsh -NoProfile -File .github\scripts\validate-instructions.ps1
```

Or invoke `/hip-validate` in Copilot Chat. The validator flags unfilled `[DATE]` placeholders, retired `§` cross-reference syntax, missing `## Contents` tables on 5+-section instruction files, malformed prompt/agent YAML frontmatter, and broken relative markdown links. Exit code is non-zero on failure, so it can be wired into CI or a pre-commit hook.

---

## Scaling Up

As your project grows, the instruction system scales horizontally (more modules) and vertically (deeper hierarchies).

### Adding Modules

Each new directory that contains logic the AI should reason about gets its own `.hi/instruct.md`. Follow the template in [Step 2 — Add Your Modules](#step-2--add-your-modules). Keep each file tightly scoped — only rules unique to that module.

### Going Deeper (Submodules)

When a module becomes large enough to have its own internal structure (e.g., `backend/api/`, `backend/services/`, `backend/data/`), add `.hi/instruct.md` files at each sub-level. The deepest file always wins.

**Signal to split**: if a single `.hi/instruct.md` has more than ~10 meaningful rules and its directory has clear sub-domains, split it.

### Large Teams

For teams with distinct ownership boundaries, scope `.hi/instruct.md` files to ownership boundaries — not just directory depth. Each team’s AI context stays self-contained.

### Keeping the Index Healthy

Run `/hip-update-index` after every significant change. A stale `index.md` defeats the purpose of the system — the AI will reference outdated section locations or miss new ones entirely.

### When Not to Add Depth

- Do not create `.hi/instruct.md` files for trivial directories (generated output, empty stubs, single-file utilities)
- A `.hi/instruct.md` must earn its place by providing rules not covered by its parent
- Start at the module level; add depth only when the parent’s rules no longer fit
