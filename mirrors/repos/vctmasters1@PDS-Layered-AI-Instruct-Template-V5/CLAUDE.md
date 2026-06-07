# CLAUDE.md — Claude Code pointer

> Claude Code auto-discovers `CLAUDE.md` at the repository root (and additional `CLAUDE.md` files in subdirectories). This file is a **pointer** — the authoritative rules live in [`.ai/`](.ai/) and per-directory `.ai/instruct.md` files. Do not duplicate rules into `CLAUDE.md`.

## Project rules location

This project uses the **Depth-Priority Hierarchical AI-INSTRUCT V5** system. **The deepest `.ai/instruct.md` always wins.**

Before suggesting any change, read in this order:

1. [.github/dev-specs.md](.github/dev-specs.md) — **CRITICAL**: Are we in Template Development or Production mode? Then: developer OS, shell, language versions, frameworks.
2. [.github/copilot-instructions.md](.github/copilot-instructions.md) — meta: how the layering works.
3. [.hi/index.md](.hi/index.md) — master index of every instruction section.
4. [.hi/instruct.md](.hi/instruct.md) — workspace-root authority.
5. `[current-directory]/.hi/instruct.md` and every ancestor — **the deepest is authoritative**, shallower files are background context only.

## Cross-cutting rules

| Topic | Canonical file |
|-------|---------------|
| Naming, file organization | [.hi/conventions.md](.hi/conventions.md) |
| Archive / never-delete / never-reset-db | [.hi/maintenance.md](.hi/maintenance.md) |
| Credentials, `.env`, `.gitignore` | [.hi/credentials.md](.hi/credentials.md) |

## Do not

- Do not put project rules into this `CLAUDE.md` — they belong in the appropriate `.hi/` file.
- Do not duplicate content from `.hi/` here. If Claude Code needs additional context, add a one-line pointer that links to the canonical file.
- If you create per-module `CLAUDE.md` files, keep them as pointers to the matching `[module]/.hi/instruct.md` — never restate rules.
