# Turbo

Turbo is a modular collection of Claude Code skills — each skill teaches Claude a specific dev workflow. Skills connect into larger pipelines like `/finalize` and `/review-pr`. See [README.md](README.md) for the full overview and dependency graph.

## Project Structure

```
skills/<skill-name>/
├── SKILL.md              # Skill definition (YAML frontmatter + markdown body)
├── scripts/              # Optional supporting scripts
├── references/           # Optional reference documentation
└── assets/               # Optional templates or boilerplate
```

Each skill is self-contained. Skills compose other skills to any depth via `/skill-name` invocations. The key distinction is between analysis skills (return structured findings without acting) and workflow skills (compose analysis skills and act on results).

@SKILL-CONVENTIONS.md

## Key Files

- `~/.turbo/config.json` — User-level configuration (repoMode, excludeSkills, lastUpdateHead, configVersion, oracle settings)
- `~/.turbo/repo/` — Local clone or fork of the turbo repo (skill source for install/update)
