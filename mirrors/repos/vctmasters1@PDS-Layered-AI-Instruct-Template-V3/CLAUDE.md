# CLAUDE.md — Claude Code pointer

> Claude Code auto-discovers `CLAUDE.md` at the repository root (and additional `CLAUDE.md` files in subdirectories). This file is a **pointer** — the authoritative rules live in [`.ai/`](.ai/) and per-directory `.ai/instruct.md` files. Do not duplicate rules into `CLAUDE.md`.

## Project rules location

This project uses the **Depth-Priority Hierarchical AI-INSTRUCT V3** system. **The deepest `.ai/instruct.md` always wins.**

Before suggesting any change, read in this order:

1. [.github/copilot-instructions.md](.github/copilot-instructions.md) — meta: how the layering works.
2. [.github/dev-specs.md](.github/dev-specs.md) — developer OS, shell, language versions, frameworks. Read at session start before suggesting commands or paths.
3. [.ai/index.md](.ai/index.md) — master index of every instruction section.
4. [.ai/instruct.md](.ai/instruct.md) — workspace-root authority.
5. `[current-directory]/.ai/instruct.md` and every ancestor — **the deepest is authoritative**, shallower files are background context only.

## Cross-cutting rules

| Topic | Canonical file |
|-------|---------------|
| Naming, file organization | [.ai/conventions.md](.ai/conventions.md) |
| Archive / never-delete / never-reset-db | [.ai/maintenance.md](.ai/maintenance.md) |
| Credentials, `.env`, `.gitignore` | [.ai/credentials.md](.ai/credentials.md) |

## Do not

- Do not put project rules into this `CLAUDE.md` — they belong in the appropriate `.ai/` file.
- Do not duplicate content from `.ai/` here. If Claude Code needs additional context, add a one-line pointer that links to the canonical file.
- If you create per-module `CLAUDE.md` files, keep them as pointers to the matching `[module]/.ai/instruct.md` — never restate rules.
