# Project Conventions

## After Making Changes

After modifying code, run:

- `npm run ci` — syntax + lint + format + tests

See [DEVELOPMENT.md](DEVELOPMENT.md) for all available scripts.

See [RELEASE.md](RELEASE.md) for the release process.

<!-- END-SHARED -->

## Upstream Adaptation Tracking

Skills are adapted from two upstream repos:

- **Anthropic**: `https://github.com/anthropics/claude-plugins-official` — local mirror at `~/projects/claude-plugins-official`
- **OpenAI**: `https://github.com/openai/skills` — local mirror at `~/projects/skills`

Last upstream check: **2026-04-30**

- Anthropic checked up to commit `0742692`
- OpenAI checked up to commit `fb7b56d`

### How to check for updates

1. **Sync local mirrors** — `cd ~/projects/claude-plugins-official && git pull --ff-only` and the same for `~/projects/skills`. Confirm `git status -sb` shows no drift before comparing.
2. **List commits since last check** — `git log --oneline <last-sha>..HEAD` in each mirror.
3. **Filter to adapted skills** — restrict the log with `-- <paths>` for plugins/folders that map to skills in this repo. Current mapping:
   - `plugins/pr-review-toolkit/` → `code-review`, `comment-analyzer`, `silent-failure-hunter`, `test-analyzer`, `type-design-analyzer`, `review-toolkit`
   - `plugins/code-simplifier/` → `code-simplifier`
   - `plugins/feature-dev/` → `feature-dev`
   - `plugins/frontend-design/` → `frontend-design`, `frontend-layout`
   - `plugins/mcp-server-dev/` → `mcp-server-dev`
   - Any OpenAI `skills/.curated/<name>/` whose name appears under `skills/` here.
4. **Inspect each candidate commit** — read the diff (`git show <sha> -- <path>`) and decide whether it touches content we actually carry (our SKILL.md files are often condensed single-file versions, so deep-reference-only changes may be no-ops).
5. **Look for newly added skills** — `git log --diff-filter=A --name-only --pretty=format: <last-sha>..HEAD -- 'plugins/*/skills/*/SKILL.md'` (Anthropic) and the equivalent under `skills/.curated/` (OpenAI). Evaluate each new skill for VS Code Copilot fit before adapting.
6. **Record the new SHAs and date** above after the check completes, regardless of whether any sync was needed.

### Skills evaluated and skipped

- `session-report` (Anthropic, added 2026-04) — depends on reading `~/.claude/projects` Claude Code transcripts; not portable to VS Code Copilot.
