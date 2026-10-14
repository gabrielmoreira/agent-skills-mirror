# CLAUDE.md

## Project Overview

Public Claude Code plugin marketplace for the Maxa organization. See [README.md](README.md) for repository structure, installation, testing, evaluations, and contributing guidelines.

### Plugin naming convention

`maxa-` prefix + domain noun, one plugin per product line. Different product lines get their own plugin entry, not a shared umbrella.

- Plugin names start with `maxa-`.
- For the main specification, use `maxa-spec` in plugin, file and command names.

Plugin names are user-facing identifiers — they appear in `/plugin install`, `enabledPlugins`, `pluginConfigs`, and skill permission rules. Settle on a name before the plugin is published.

Current: `maxa-spec`. Planned: `maxa-pipelines`, `maxa-preflight`, `maxa-analyst`.

## Git and Source Control

GitHub with trunk-based development. Short-lived feature branches off `main`, merged frequently, deleted after merge.

### Commits

[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) enforced. Format: `<type>[optional scope]: <description>`.

Types: `feat`, `fix`, `docs`, `refactor`, `chore`.

### Branches

- Linear-tracked: `feature/<linear-id>-<description>` (e.g. `feature/studio-894-description`)
- Other: `<username>/<type>/<description>` (e.g. `johnd/fix/database-timeout`)

### Pull requests

Rebase over `main` before submitting. Reference Linear tasks in PR title or branch name — `Fixes STUDIO-123` auto-closes the task on merge.

### Releases

[Google Release Please](https://github.com/googleapis/release-please) automates versioning and changelogs from commit history. `feat:` → minor, `fix:` → patch, `BREAKING CHANGE:` → major.
