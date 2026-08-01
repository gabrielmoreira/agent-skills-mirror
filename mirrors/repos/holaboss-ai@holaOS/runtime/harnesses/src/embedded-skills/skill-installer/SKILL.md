---
name: skill-installer
description: Install workspace skills from curated sources or import open-source skills from GitHub.
---

# Skill Installer

Use this skill to install workspace skills into the workspace-local `skills/` directory.

A freshly installed skill is usable **immediately, in this same run**: `skill({ name: "<id>" })` reads the folder off disk on every call. What waits for the next run is only the skill *listing* in your capability manifest — the skill itself is already there. Never tell the user to start a new conversation to use what you just installed; if they asked you to install it and use it, load it and carry on.

## Import an open-source skill from GitHub (preferred)

Open-source skills (e.g. `github.com/anthropics/skills`) are just `SKILL.md` folders in the same format used here, so they can be imported whole. Use the runtime endpoint — it fetches the entire folder (`SKILL.md` plus bundled `scripts/`, `references/`, `assets/`), maps foreign frontmatter (`allowed-tools` → `holaboss_granted_tools`, aligns `name` to the installed id), and writes it under `skills/<id>/`:

- Preview (no write): `POST /api/v1/workspaces/{workspaceId}/skills/import-github/preview` with `{ "url": "<github folder or SKILL.md URL>" }` — returns the parsed name, description, granted tools, and file list so you can confirm before installing.
- Install: `POST /api/v1/workspaces/{workspaceId}/skills/import-github` with the same body.

Accepts `github.com/<owner>/<repo>/tree/<ref>/<path>` (folder), `.../blob/<ref>/<path>/SKILL.md` (single file), or a bare repo. Pass an optional `"ref"` for a specific branch/tag/commit (defaults to the repo's default branch). Skills whose bundled scripts assume tools this sandbox lacks still install and work as pure guidance.

## What to tell the user afterwards

Its **name and how to use it** — the id they invoke it by, the one-line description, and what to say to put it to work. The install response also carries the written file list; that is for your own verification, not something to report. "Installed `SKILL.md`, `scripts/render.py`" tells them nothing they can act on.

## Notes
1. Install each workspace skill under `skills/<skill-id>/` with its `SKILL.md` plus any helper files. For skills you author by hand, create these files directly with the Write tool.
2. Guidance only: do not install workspace skills into `runtime/harnesses/src/embedded-skills/`. Do not install into `$CODEX_HOME/skills` unless the user explicitly asks for a global install rather than a workspace install.
