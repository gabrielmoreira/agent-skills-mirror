---
name: validate-skills
description: Validates skills in this repo against agentskills.io spec and Claude Code best practices. Use via /validate-skills command.
license: MIT
metadata:
  author: Callstack
  tags: validation, linting, skill-authoring
---

# Validate Skills

Validate all skills in `skills/` against the agentskills.io spec and Claude Code best practices.

## Validation Checklist

For each skill directory, verify:

### Spec Compliance (agentskills.io)

| Check | Rule |
|-------|------|
| `name` format | 1-64 chars, lowercase alphanumeric + hyphens, no leading/trailing/consecutive hyphens |
| `name` matches directory | Directory name must equal `name` field |
| `description` length | 1-1024 characters, non-empty |
| Optional fields valid | `license`, `metadata`, `compatibility` if present |

### Best Practices (Claude Code)

| Check | Rule |
|-------|------|
| Description format | Third person, describes what + when to use |
| Body length | Under 500 lines |
| Loading is one-level deep | `SKILL.md` is the only progressive-disclosure entry point: every reference file must be reachable from `SKILL.md`. References may cross-link each other for navigation (see note below). |
| Links are markdown | Use `[text](path)` not bare filenames |
| No redundancy | Don't repeat description in body |
| Concise | Only add context Claude doesn't already have |

> **One-level-deep vs. cross-linking.** The one-level-deep rule targets *progressive-disclosure loading chains* — a reference that can only be discovered by loading another reference first (`SKILL.md` → `a.md` → `b.md`, where `b.md` is not linked from `SKILL.md`). That is a defect: it hides content from the loader.
>
> It does **not** forbid *navigational* cross-links. Per [AGENTS.md](../../../AGENTS.md), reference files end with a "Related Skills" footer linking sibling references, and this is required. A cross-link is fine as long as both endpoints are also reachable directly from `SKILL.md`. Only flag a reference that is reachable *exclusively* through another reference.

## How to Run

1. Find all skill directories:
   ```bash
   fd -t d -d 1 . skills/
   ```

2. For each skill, read `SKILL.md` and check against the rules above

3. Report issues in this format:
   ```
   ## Validation Results

   ### skills/example-skill
   - [PASS] name format valid
   - [FAIL] name "example" doesn't match directory "example-skill"
   - [PASS] description length OK (156 chars)
   ```

## References

- [agentskills.io spec](https://agentskills.io/specification)
- [Claude Code best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
