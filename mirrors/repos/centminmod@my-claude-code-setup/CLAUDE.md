# CLAUDE.md

<!-- Project-specific context only. Behavioral rules: .claude/rules/core-rules.md -->
<!-- Run /init to auto-populate (or CLAUDE_CODE_NEW_INIT=1 for interactive mode) -->
<!-- Keep under 200 lines. If removing a line wouldn't cause mistakes, cut it -->

## Project Overview

- Name: my-claude-code-setup
- Description: Template repository providing CLAUDE.md templates, memory bank system, hooks, skills, subagents, and MCP server configurations for Claude Code projects
- This is a template repo — no application code. Users fork/copy files to their own projects.

## CLAUDE.md Templates

This repo provides 3 CLAUDE.md templates following official Anthropic best practices:

| Template | Lines | Philosophy |
|----------|-------|------------|
| `CLAUDE-template-1.md` | ~101 | Compact self-contained + memory resilience |
| `CLAUDE-template-2.md` | ~153 | Memory bank headline + dual memory |
| `CLAUDE-template-3.md` | ~105 | Progressive disclosure native (this file's format) |

For migrating an existing CLAUDE.md to a new template, see `CLAUDE-migrate-to-new-template.md`.

## Tools

Use `rg` not grep, `fd` not find. `tree` is not installed.

* Ignore GEMINI.md and GEMINI-*.md files

## Rules Dependency

This template requires `.claude/rules/core-rules.md` for behavioral rules. If `.claude/rules/` is missing or empty, alert the user and direct them to https://github.com/centminmod/my-claude-code-setup to obtain the companion rules files.

---

## Memory System

This project uses a dual-memory architecture:

**Primary (git-shared):** CLAUDE-*.md files in repo root — read on demand:

| File | Read When |
|------|-----------|
| CLAUDE-activeContext.md | Session start (state and goals) |
| CLAUDE-patterns.md | Before implementing (code patterns) |
| CLAUDE-decisions.md | Before design choices (ADRs) |
| CLAUDE-troubleshooting.md | When debugging (known fixes) |
| CLAUDE-config-variables.md | When touching config |

**Shadow (machine-local):** Native auto memory mirrors key content for resilience:

| Auto Memory File | Mirrors | Purpose |
|-----------------|---------|---------|
| memory/MEMORY.md | Index of all memory bank files | Always loaded (200 lines) |
| memory/patterns.md | CLAUDE-patterns.md | Survives CLAUDE.md reset |
| memory/architecture.md | CLAUDE-decisions.md | Survives CLAUDE.md reset |
| memory/build.md | Build, Test & Verify section | Survives CLAUDE.md reset |

All optional — check existence first. Exclude CLAUDE.md and CLAUDE-*.md from commits.

<!-- BACKUP TIP: Create a private git repo for memory bank backups:
     rsync -av ./CLAUDE.md ./CLAUDE-*.md ./.claude/ ~/my-project-memory-backup/
     This keeps CLAUDE-*.md version-controlled privately while excluded from the public repo. -->

### Sync Workflow

After significant work: update CLAUDE-*.md files, then sync key content to auto memory topic files.

If CLAUDE.md is ever reset or wiped, auto memory retains project knowledge — check `/memory` to recover context.

### Backups

When asked to backup, copy CLAUDE.md, CLAUDE-*.md files, and `.claude/` settings to the specified backup directory.

---

## Context Layers

| Layer | Location | Loads | Shared | Resilient |
|-------|----------|-------|--------|-----------|
| Project context | This file | Always | Git | No |
| Core rules | `.claude/rules/core-rules.md` | Always | Git | Yes |
| Auto memory | memory/MEMORY.md | Always (200 lines) | No | Yes |
| Auto memory topics | memory/*.md | On demand | No | Yes |
| Path-scoped rules | `.claude/rules/*.md` | Matching files | Git | Yes |
| User rules | `~/.claude/rules/*.md` | Always | No | Yes |
| Skills | `.claude/skills/` | On demand | Git | Yes |
| Personal overrides | `CLAUDE.local.md` | Always | No | Local |
| Memory bank | CLAUDE-*.md | On demand | Git | No |

<!-- To share rules across projects: ln -s ~/shared-rules .claude/rules/shared -->

Use `/memory` to inspect loaded files. Root CLAUDE.md survives `/compact`.

## Claude Code Official Documentation

When working on Claude Code features (hooks, skills, subagents, MCP servers), use the `claude-code-guide` subagent (natively built into Claude Code) for questions about Claude Code CLI features, hooks, slash commands, MCP servers, settings, IDE integrations, Claude Agent SDK, and Claude API usage.
