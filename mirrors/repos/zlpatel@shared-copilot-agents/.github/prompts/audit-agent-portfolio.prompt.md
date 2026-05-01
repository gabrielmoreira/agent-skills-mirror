---
description: "Audit all Copilot agents, instructions, skills, prompts, and hooks in the workspace for anti-patterns, context waste, and improvement opportunities."
agent: "copilot-agent-architect"
tools: [read, search]
---

Perform a comprehensive health check of ALL Copilot customization files in this workspace. This is a read-only audit — do not edit any files.

## Step 1 — Discover All Customization Files

Search the entire workspace for:
- `*.agent.md` in `.github/agents/` folders
- `*.instructions.md` in `.github/instructions/` folders
- `*.prompt.md` in `.github/prompts/` folders
- `SKILL.md` in `.github/skills/*/` folders
- `*.json` in `.github/hooks/` folders
- `copilot-instructions.md` or `AGENTS.md` at repo roots or `.github/`

List every file found with its path and line count.

## Step 2 — Context Budget Analysis

For each file, classify its context loading behavior:

| Loading | Trigger |
| --- | --- |
| **Always-on** | `applyTo: "**"` or workspace instructions |
| **File-scoped** | `applyTo` with specific glob pattern |
| **On-demand** | Loaded via `description` keyword match only |
| **Agent-scoped** | Plain `.md` files in `agent-knowledge/` referenced only from a specific agent's body |
| **User-invoked** | Agents, prompts, skills triggered by user |

Calculate the total line count of all always-on content. Flag if it appears excessive (guideline: always-on content should be < 30% of estimated context budget, roughly under 1500 lines combined).

## Step 3 — Anti-Pattern Scan

Check every discovered file against these anti-patterns:

| Anti-Pattern | What to Check |
| --- | --- |
| **Vague description** | Description missing or lacks specific trigger keywords |
| **Swiss-army agent** | Agent has 8+ tools or tries to do multiple unrelated jobs |
| **Context hog** | `applyTo: "**"` on a file over 200 lines |
| **Role confusion** | Description says one thing, body persona does another |
| **Missing constraints** | Agent has no DO NOT rules or Constraints section |
| **Duplicate content** | Same rules or knowledge appear in multiple files |
| **Monolithic file** | Single file over 500 lines that should be split |
| **Dead description** | Description keywords do not match how users actually phrase tasks |
| **Name mismatch** | Skill folder name does not match `name` field in frontmatter |
| **YAML syntax risk** | Unquoted descriptions containing colons, tabs in frontmatter |
| **Cross-agent contamination** | Agent-specific knowledge in an instruction file with `description:` keywords that match other agents' domains |

## Step 4 — Agent Boundary Check

For each agent, verify:
- Does it have a single, clear role?
- Does its tool list contain only what it needs?
- Does its description overlap with another agent's description?
- If it supports subagent invocation, are there circular handoff risks?

## Step 5 — Report

Present the findings as a structured report:

### Portfolio Summary
- Total files by type (agents, instructions, prompts, skills, hooks)
- Always-on context budget (total lines, percentage estimate)

### Findings Table

| File | Finding | Severity | Recommendation |
| --- | --- | --- | --- |
| (path) | (issue description) | Critical / Warning / Info | (specific fix) |

Severity definitions:
- **Critical** — Broken behavior: file won't load, YAML parse failure, or agent won't be discovered
- **Warning** — Suboptimal: context waste, missing constraints, or discoverability gap
- **Info** — Minor improvement opportunity

### Verdict
- State whether the portfolio is healthy, needs minor tuning, or needs significant refactoring
- List the top 3 highest-impact improvements to make first
