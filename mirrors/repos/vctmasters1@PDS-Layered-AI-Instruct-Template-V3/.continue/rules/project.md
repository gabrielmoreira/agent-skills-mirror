---
name: PDS Depth-Priority AI-INSTRUCT pointer
alwaysApply: true
globs:
  - "**/*"
---

# Continue compatibility — rules pointer

> Continue reads rule files from `.continue/rules/*.md`. This project's authoritative rules live in [`.ai/`](../../.ai/) and per-directory `.ai/instruct.md` files. The files in this directory are pointers — they tell Continue where to look so its agent behaves the same way GitHub Copilot does in this repo.

## Project rules location

This project uses the **Depth-Priority Hierarchical AI-INSTRUCT V3** system. The rule files are **not** stored in `.continue/rules/` — they are stored under `.ai/` and in per-directory `.ai/instruct.md` files. **The deepest `.ai/instruct.md` always wins.**

Before suggesting any change, read in this order:

1. [`.github/copilot-instructions.md`](../../.github/copilot-instructions.md) — meta: how the layering works.
2. [`.github/dev-specs.md`](../../.github/dev-specs.md) — developer OS, shell, language versions, frameworks. Read at session start before suggesting commands or paths.
3. [`.ai/index.md`](../../.ai/index.md) — master index of every instruction section.
4. [`.ai/instruct.md`](../../.ai/instruct.md) — workspace-root authority.
5. `[current-directory]/.ai/instruct.md` and every ancestor — **the deepest is authoritative**, shallower files are background context only.

## Cross-cutting rules

| Topic | Canonical file |
|-------|---------------|
| Naming, file organization | [`.ai/conventions.md`](../../.ai/conventions.md) |
| Archive / never-delete / never-reset-db | [`.ai/maintenance.md`](../../.ai/maintenance.md) |
| Credentials, `.env`, `.gitignore` | [`.ai/credentials.md`](../../.ai/credentials.md) |

## Do not

- Do not invent a new `.continue/rules/*.md` file with project rules in it — those rules belong in the appropriate `.ai/` file. The `.continue/rules/` directory is a pointer layer only.
- Do not duplicate content from `.ai/` into Continue rules. If Continue needs context, add a one-line pointer here that links to the canonical file.
