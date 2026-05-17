# last30days Skill

Agent Skills package for researching any topic across Reddit, X, YouTube, and web. Installable across Claude Code (most common host), Codex, Cursor, GitHub Copilot, Gemini CLI, and 50+ other [Agent Skills](https://agentskills.io) hosts. Python scripts with multi-source search aggregation.

## Structure
- `skills/last30days/SKILL.md` — canonical skill definition
- `skills/last30days/scripts/last30days.py` — main research engine
- `skills/last30days/scripts/lib/` — search, enrichment, rendering modules
- `skills/last30days/scripts/lib/vendor/bird-search/` — vendored X search client
- `docs/solutions/` — documented solutions to past problems (bugs, best practices, workflow patterns), organized by category with YAML frontmatter (`module`, `tags`, `problem_type`)
- `CONCEPTS.md` — shared domain vocabulary (Skill, Engine, Harness, Beta channel) — relevant when orienting to the codebase or discussing project terminology

## Orientation
- This is an Agent Skills package, not a CLI tool. The product is the slash-command-invoked skill (`/last30days <topic>` in most harnesses); `scripts/last30days.py` is implementation. Claude Code is the most common host but not the only one — features must work across every harness the skill installs into.
- Feature design starts from the slash-command UX. A new engine flag with no SKILL.md integration is incomplete — the model invoking the skill won't know the flag exists.
- README and PR examples show `/last30days <topic>` first. Direct CLI invocation (`python3 scripts/last30days.py ...`) is a fallback for scripting, cron, and dev-time engine testing; label it as such, never as the primary path.
- Slash commands don't pass shell mechanics through. `/last30days OpenClaw --emit=html | pbcopy` is invalid in any harness — either use the slash form (no flags or pipes; let the model translate user intent into engine flags) or use the direct CLI form (full `python3 ...` with explicit flags and a real shell).

## Commands
```bash
# Dev/fallback: direct engine invocation (scripting, cron, or engine testing only)
python3 skills/last30days/scripts/last30days.py "test query" --emit=compact
npx skills add . -g -y   # one-time: symlink this repo into every detected harness's skill dir

## Rules
- `lib/__init__.py` must be bare package marker (comment only, NO eager imports)
- One-time setup: `npx skills add . -g -y` creates symlinks from each detected harness's skill dir to this repo. Edits in the working tree propagate live to every harness — no re-deploy step needed.
- Git remote: origin = public (`mvanhorn/last30days-skill`)

## Beta channel

Experimental changes get tested on `mvanhorn/last30days-skill-private`, which installs as a parallel `/last30days-beta` slash command. Beta-only changes never ship to public without a review PR here. Workflow guide lives at `BETA.md` in the private repo. Plan that established this setup: `docs/plans/2026-04-17-005-feat-beta-skill-from-private-repo-plan.md`.
