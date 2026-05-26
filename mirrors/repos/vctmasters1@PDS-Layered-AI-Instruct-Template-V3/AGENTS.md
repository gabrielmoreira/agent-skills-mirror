# AGENTS.md — Entry Point for AI Coding Agents

> This file is the **discovery anchor** for any AI agent or tool entering this repository. It points to the authoritative instruction system; it does **not** restate rules.
> This repository is a **template framework**. Placeholder values in authority files are expected until onboarding fills them.

## Where the rules live

This project uses the **Depth-Priority Hierarchical AI-INSTRUCT V3** system. Rules are stored as per-directory `.ai/instruct.md` files. **Deeper always wins.**

Start here, in this order:

1. [.github/copilot-instructions.md](.github/copilot-instructions.md) — META: how the layering system works (read once per session).
2. [.github/dev-specs.md](.github/dev-specs.md) — Platform, shell, language, frameworks. Read at session start before suggesting commands or paths; if still template-empty, run `/ai-onboard` or ask focused follow-up questions to fill/confirm it.
3. [.ai/index.md](.ai/index.md) — Master index of every instruction section. Jump from here to the canonical source for any topic.
4. [.ai/instruct.md](.ai/instruct.md) — Root-level project authority.
5. `[module]/.ai/instruct.md` — Module-level authority. Authoritative when working inside that module.

## Quick reference

| If you are looking for… | Go to |
|-------------------------|-------|
| Naming and file organization | [.ai/conventions.md](.ai/conventions.md) |
| Archive / never-delete / never-reset-db | [.ai/maintenance.md](.ai/maintenance.md) |
| Credentials, `.env`, `.gitignore` | [.ai/credentials.md](.ai/credentials.md) |
| Host vs. container isolation (never silently mutate host) | [.ai/environment.md](.ai/environment.md) |
| Full topic map | [.ai/index.md](.ai/index.md) |

## Tool compatibility

This repo's instruction system is designed primarily for **GitHub Copilot** (which reads `.github/copilot-instructions.md` automatically). It is also usable with:

- **OpenAI Codex CLI** — auto-discovers this `AGENTS.md`.
- **Aider** — does **not** auto-discover `AGENTS.md`. Point it at the instruction files explicitly via `--read .ai/conventions.md --read .ai/instruct.md` (or list them under `read:` in `.aider.conf.yml`).
- **Cursor** — pre-configured via [`.cursor/rules/project.mdc`](.cursor/rules/project.mdc), a pointer rule that directs Cursor to read the same `.ai/` hierarchy. Do not duplicate rules into `.cursor/rules/`.
- **Claude Code** — pre-configured via [`CLAUDE.md`](CLAUDE.md) at the repo root, a pointer file that directs Claude Code to read the same `.ai/` hierarchy. Do not put project rules into `CLAUDE.md`.
- **Continue** — pre-configured via [`.continue/rules/project.md`](.continue/rules/project.md), a pointer rule that directs Continue to read the same `.ai/` hierarchy. Do not duplicate rules into `.continue/rules/`.
- **Cline** — pre-configured via [`.clinerules/project.md`](.clinerules/project.md), a pointer rule that directs Cline to read the same `.ai/` hierarchy. Do not duplicate rules into `.clinerules/`.

Other agents not listed above can be pointed at the files listed above via their own configuration mechanism — add a new pointer file following the same pattern.

For any tool: the contract is "read the files referenced above; the deepest `.ai/instruct.md` in your current working directory is authoritative."

## Adopting this template

See [TEMPLATE-USAGE.md](TEMPLATE-USAGE.md) for setup steps.
Use `/ai-onboard` to convert template placeholders into project-specific values, including `.github/dev-specs.md`.
