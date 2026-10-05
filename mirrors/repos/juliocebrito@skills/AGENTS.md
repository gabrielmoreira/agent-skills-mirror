# AGENTS.md

Agent skills for AI coding assistants (Claude Code, Cursor, GitHub Copilot, OpenCode…), installable with the [skills CLI](https://skills.sh).

## Structure

```
skills/<name>/
  SKILL.md    # instructions the agent loads
  README.md   # user-facing documentation
docs/         # project documentation
```

## Conventions

- Write everything in English: skills, READMEs, docs and commits.
- Each skill lives in `skills/<name>/`, where `<name>` is lowercase kebab-case and matches the `name` field in its `SKILL.md`.
- `SKILL.md` starts with YAML frontmatter: `name`, `description`, `license: MIT` and `metadata.version`.
- The `description` says what the skill does and when to use it: it is what the agent reads to decide whether to load the skill.
- Bump `metadata.version` (semver) whenever a skill's behaviour changes.
- When adding or renaming a skill, update the table in the root [README.md](README.md).

## Validation

Check that the CLI detects the skill, then install it locally and try it in at least one assistant before committing:

```bash
npx skills add ./ --list            # lists the skills found, installs nothing
npx skills add ./ --skill <name>
```
