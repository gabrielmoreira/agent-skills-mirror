# AGENTS.md — Entry Point for AI Coding Agents

> **READ THIS FIRST.** This file is the **discovery anchor** for any AI agent or tool entering this repository.
> This repository uses the **Depth-Priority Hierarchical AI-INSTRUCT V6** system with unified `.hi/` governance and **Routing Gateway** at its core.

## 🚀 The Core Feature: Routing Gateway

**Every major workflow in this project flows through `/ai-route`** — a central orchestration layer that:

✅ Resolves which `.hi/instruct.md` is authoritative for your current scope  
✅ Applies governance rules automatically  
✅ Routes to the domain manager/supervisor that owns that scope  
✅ Logs all decisions for audit trails  
✅ Halts gracefully on conflicts  

**This is not optional.** It is the **defining feature** that makes depth-priority hierarchy practical at scale.

→ **Start with [The Routing Gateway](.github/copilot-instructions.md#the-routing-gateway--core-orchestration-layer)** in `.github/copilot-instructions.md` (2-min read)

## Where the rules live

Rules are stored as per-directory `.hi/instruct.md` files. **Deeper always wins.**

Start here, in this order:

1. **[The Routing Gateway](.github/copilot-instructions.md#the-routing-gateway--core-orchestration-layer)** in `.github/copilot-instructions.md` — WHY routing exists, how it works, which workflows use it (start here 🚀)
2. [.github/copilot-instructions.md](.github/copilot-instructions.md) — META: complete layering system (read once per session)
3. [.github/dev-specs.md](.github/dev-specs.md) — **CRITICAL**: Read the Project Mode field (Template Development vs Production) before any other decision. Then: Platform, shell, language, frameworks. If template-empty, run `/hip-onboard` to fill values.
4. [.hi/index.md](.hi/index.md) — Master index of every instruction section. Jump from here to the canonical source for any topic.
5. [.hi/instruct.md](.hi/instruct.md) — Root-level project authority. Confirms the [Routing & Orchestration Gateway](.hi/instruct.md#routing--orchestration-gateway) section.
6. `[module]/.hi/instruct.md` — Module-level authority. Authoritative when working inside that module.

## Quick reference

| If you are looking for… | Go to |
|-------------------------|-------|
| Naming and file organization | [.hi/conventions.md](.hi/conventions.md) |
| Archive / never-delete / never-reset-db | [.hi/maintenance.md](.hi/maintenance.md) |
| Credentials, `.env`, `.gitignore` | [.hi/credentials.md](.hi/credentials.md) |
| Host vs. container isolation (never silently mutate host) | [.hi/environment.md](.hi/environment.md) |
| Full topic map | [.hi/index.md](.hi/index.md) |

## **CRITICAL: Import/Merge Workflows are Governed**

⚠️ **If the user mentions any of these, you MUST use `/hip-import-execute` — DO NOT run ad-hoc `git clone`, `Move-Item`, `cp`, or manual directory copies:**

- "clone" + project/repo reference
- "import" + external project name
- "merge" + another project
- "adopt" + external codebase
- "migrate" + project / code
- "consolidate" + multiple projects
- "integrate" + external repo

**Why?** Ad-hoc imports cause:
- **Registry corruption** — naming violations, module conflicts
- **Credential leakage** — `.env` files committed unintentionally
- **Authority drift** — module `.ai/instruct.md` rules ignored
- **Audit trail loss** — no record of what was merged or why

**Correct flow:** Recognize pattern → `invoke /hip-import-execute` → orchestration layer handles Phase 0 (validation) + Phases 1-6 (integration).

See [Governed Workflows section](.github/copilot-instructions.md#governed-workflows--importmerge-pattern-guard) in copilot-instructions.md for full details.

## Tool compatibility

This repo's instruction system is designed primarily for **GitHub Copilot** (which reads `.github/copilot-instructions.md` automatically). It is also usable with:

- **OpenAI Codex CLI** — auto-discovers this `AGENTS.md`.
- **Aider** — does **not** auto-discover `AGENTS.md`. Point it at the instruction files explicitly via `--read .hi/conventions.md --read .hi/instruct.md` (or list them under `read:` in `.aider.conf.yml`).
- **Cursor** — pre-configured via [`.cursor/rules/project.mdc`](.cursor/rules/project.mdc), a pointer rule that directs Cursor to read the same `.hi/` hierarchy. Do not duplicate rules into `.cursor/rules/`.
- **Claude Code** — pre-configured via [`CLAUDE.md`](CLAUDE.md) at the repo root, a pointer file that directs Claude Code to read the same `.hi/` hierarchy. Do not put project rules into `CLAUDE.md`.
- **Continue** — pre-configured via [`.continue/rules/project.md`](.continue/rules/project.md), a pointer rule that directs Continue to read the same `.hi/` hierarchy. Do not duplicate rules into `.continue/rules/`.
- **Cline** — pre-configured via [`.clinerules/project.md`](.clinerules/project.md), a pointer rule that directs Cline to read the same `.hi/` hierarchy. Do not duplicate rules into `.clinerules/`.

Other agents not listed above can be pointed at the files listed above via their own configuration mechanism — add a new pointer file following the same pattern.

For any tool: the contract is "read the files referenced above; the deepest `.hi/instruct.md` in your current working directory is authoritative."

## Adopting this template

See [TEMPLATE-USAGE.md](TEMPLATE-USAGE.md) for setup steps.
Use `/hip-onboard` to convert template placeholders into project-specific values, including `.github/dev-specs.md`.

## Autonomous layer (opt-in, disabled by default)

This template ships a **lightweight autonomous orchestration layer** under [`.hi/autonomous/`](.hi/autonomous/). It composes the existing 19-agent network — it adds no new authority and **no new agents**. It is **disabled by default**.

### How to enable

1. Read, in this order: [`.hi/autonomous/safety-guardrails.md`](.hi/autonomous/safety-guardrails.md), [`.hi/autonomous/orchestrator.md`](.hi/autonomous/orchestrator.md), [`.hi/autonomous/task-queue.md`](.hi/autonomous/task-queue.md).
2. Edit [`.hi/autonomous/autonomy-config.yaml`](.hi/autonomous/autonomy-config.yaml) and set `enabled: true`.
3. Keep `human_approval.mode: "always"` for the first runs.
4. Try the worked example: [`workflow-examples/feature-implementation.md`](.hi/autonomous/workflow-examples/feature-implementation.md).
5. Invoke with [`/hip-autonomous-start`](.github/.hi/prompts/hip-autonomous-start.prompt.md). The command refuses if the master switch is off.

### Limitations (intentional)

- Single goal at a time (`max_parallel_workers: 1`).
- Hard ceilings: 25 steps, 30 minutes, 20 files modified per run.
- Cannot edit `.ai/instruct.md`, `.ai/governance/`, `.ai/index.md`, `.env`, secrets, or DB schemas. Those are reserved for human-driven flows (`/ai-reflect`, `/ai-update-index`, `pds-man-curator`).
- Cannot invoke `pds-man-curator` or `pds-meta-learner` — governance edits stay human-driven.
- Heartbeat re-reads of the scope authority and guardrails files; any drift halts the run.
- All standing safety contracts apply unchanged: archive-first, never-reset-db, credential isolation, host isolation, depth-priority instructions.
- A `.ai/PAUSE` file halts every run at the next iteration.

If any limitation gets in the way, the correct response is **not** to relax the orchestrator — it is to keep using the existing slash commands directly.
