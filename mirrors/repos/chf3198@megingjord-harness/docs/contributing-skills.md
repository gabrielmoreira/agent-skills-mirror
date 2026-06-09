# Skill Development Guide

Skills are self-contained capability modules. Each has a `SKILL.md` descriptor
and, where needed, a supporting script in `scripts/global/`.

## Universal vs personal skills

Skills are categorised in `skills/.plugin-triage.json`:

| Category      | Ships via     | Runtime target                     |
| ------------- | ------------- | ---------------------------------- |
| **Universal** | `plugin.json` | All consumers (deployed globally)  |
| **Personal**  | `deploy.sh`   | `~/.copilot/` on this machine only |

## Skill directory layout

```
skills/<name>/
├── SKILL.md          # Required — descriptor with YAML frontmatter
└── (supporting files as needed, each ≤100 lines)
```

## SKILL.md format

```markdown
---
name: skill-name
description: One-line description ≤80 characters
version: 1.0.0
runtime: copilot | claude | codex | all
category: governance | routing | wiki | fleet | utility
---

# skill-name — Title

## Purpose

What problem this skill solves and for whom.

## Scope

Which files, subsystems, or operations it touches.

## Constraints

Edge cases, limitations, incompatibilities.

## Instructions

Step-by-step guidance the LLM follows when invoking this skill.

## Verification

How to confirm the skill works after deployment.
```

## Adding a universal skill

1. Create `skills/<name>/SKILL.md` with valid YAML frontmatter
2. Add entry to `plugin.json` → `skills` array
3. Add to `skills/.plugin-triage.json` → `universal` list
4. Run `npm run validate:triage` → must pass with no errors
5. Run `npm run validate:compat` if `plugin.json` changed
6. Branch → PR → squash-merge → `npm run deploy:apply`

## Adding a personal skill

1. Create `skills/<name>/SKILL.md`
2. Add to `skills/.plugin-triage.json` → `personal` list
3. **Do NOT** add to `plugin.json` (personal skills are machine-local only)
4. Run `npm run validate:triage` → must pass

## Testing plugin installation

1. Push your branch to `origin`
2. In VS Code: **Chat: Install Plugin From Source**
3. Paste the branch Git URL (e.g. `https://github.com/chf3198/megingjord-harness#your-branch`)
4. Confirm skills appear in the Copilot chat suggestion list
5. Exercise the skill; verify output matches `SKILL.md § Verification`

## Cross-tool compatibility

| Runtime         | Detection path                         | Install mechanism                      |
| --------------- | -------------------------------------- | -------------------------------------- |
| VS Code Copilot | `plugin.json` (root)                   | Plugin reload (`Chat: Refresh Skills`) |
| Claude Code     | `.claude-plugin/plugin.json` (symlink) | `npm run deploy:claude:apply`          |
| GitHub Copilot  | `.github/plugin/plugin.json` (symlink) | Plugin install                         |

All three symlinks resolve to the root `plugin.json` automatically.

## Claude Code runtime install

```bash
npm run deploy:claude:apply   # repo .claude/ → ~/.claude/
npm run sync:claude            # ~/.claude/ → repo .claude/ (pull back)
```

All skill files must be **≤100 lines** (lint-enforced). Split oversized skills
into `SKILL.md` (nav) + `SKILL-detail.md` (body) and link between them.
