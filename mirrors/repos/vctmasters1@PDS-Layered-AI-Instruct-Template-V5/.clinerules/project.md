# Cline compatibility — rules pointer

> Cline reads rule files from `.clinerules/` (a directory of markdown files) or a single `.clinerules` file. This project's authoritative rules live in [`.hi/`](../.hi/) and per-directory `.hi/instruct.md` files. The files in this directory are pointers — they tell Cline where to look so its agent behaves the same way GitHub Copilot does in this repo.

## Project rules location

This project uses the **Depth-Priority Hierarchical AI-INSTRUCT V6** system. The rule files are **not** stored in `.clinerules/` — they are stored under `.hi/` and in per-directory `.hi/instruct.md` files. **The deepest `.hi/instruct.md` always wins.**

Before suggesting any change, read in this order:

1. [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) — meta: how the layering works.
2. [`.github/dev-specs.md`](../.github/dev-specs.md) — developer OS, shell, language versions, frameworks. Read at session start before suggesting commands or paths.
3. [`.hi/index.md`](../.hi/index.md) — master index of every instruction section.
4. [`.hi/instruct.md`](../.hi/instruct.md) — workspace-root authority.
5. `[current-directory]/.hi/instruct.md` and every ancestor — **the deepest is authoritative**, shallower files are background context only.

## Cross-cutting rules

| Topic | Canonical file |
|-------|---------------|
| Naming, file organization | [`.hi/conventions.md`](../.hi/conventions.md) |
| Archive / never-delete / never-reset-db | [`.hi/maintenance.md`](../.hi/maintenance.md) |
| Credentials, `.env`, `.gitignore` | [`.hi/credentials.md`](../.hi/credentials.md) |

## Do not

- Do not invent a new `.clinerules/*.md` file with project rules in it — those rules belong in the appropriate `.hi/` file. The `.clinerules/` directory is a pointer layer only.
- Do not duplicate content from `.hi/` into Cline rules. If Cline needs context, add a one-line pointer here that links to the canonical file.

## MCP server

Cline configures MCP servers through its UI (Settings → MCP Servers → Add). Use the bundled [`pds-ai-instruct`](../.ai/mcp/README.md) server:

- **Command**: `python`
- **Args**: `-m pds_mcp`
- **Env**: `PDS_WORKSPACE=<absolute path to this workspace>`

Install once per clone: `cd .ai/mcp/python && pip install -e .` (or use the Node twin at `.ai/mcp/node/`).
