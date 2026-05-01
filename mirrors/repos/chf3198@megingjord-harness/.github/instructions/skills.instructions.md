---
applyTo: "skills/**,instructions/**,hooks/**,scripts/global/**"
---

# Global Resource Development Instructions

## This Repo vs Runtime

- **This repo** (`skills/`, `instructions/`, `hooks/`, `scripts/global/`): development source
- **`~/.copilot/`**: deployed runtime — VS Code reads skills/instructions from here
- All edits happen in this repo first, then deploy with `npm run deploy:apply`

## Editing Workflow

1. Branch: `git checkout -b skill/<name>-change` (or `hook/`, `instruction/`)
2. Edit the file in this repo
3. Test: verify agent behavior in a Copilot Chat session
4. Merge to main after validation
5. Deploy: `npm run deploy:apply`

## Skill Format (SKILL.md)

Every skill must contain:
- **Frontmatter** — name, description, argument-hint, user-invocable, disable-model-invocation
- **Purpose** — What the skill does
- **Scope boundary** — What it owns vs hands off
- **Hard constraints** — Bounded rules
- **Instructions** — Step-by-step execution logic
- **Verification** — How to confirm it worked

## Instruction Format (*.instructions.md)

- Frontmatter with `applyTo` glob pattern
- Clear scope and when-to-apply conditions
- Additive to repo-local instructions (never override)

## Deploy Safety

- Never deploy from an unmerged branch
- `npm run deploy` (dry-run) first, review the diff
- `npm run deploy:apply` creates timestamped backup automatically
- Refresh dev copies: `npm run sync` after any direct runtime changes
