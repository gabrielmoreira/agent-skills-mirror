# AGENTS.md

Guidelines for AI agents working in this repository. For full runtime context, see [CLAUDE.md](CLAUDE.md).

## Repository Overview

- **Name**: seo-geo-claude-skills — 20 SEO/GEO skills, 5 commands, shared references
- **Repository**: https://github.com/aaron-he-zhu/seo-geo-claude-skills
- **Author**: Aaron He Zhu | **License**: Apache 2.0
- **Specs**: [Agent Skills](https://agentskills.io/specification.md)
Content-first repository: skills and commands are Markdown; Claude Code hooks use a small Bash runner; `scripts/connectors/` holds zero-dependency Python-stdlib data helpers (no pip deps). Primary directories: `research/`, `build/`, `optimize/`, `monitor/`, `cross-cutting/`, `commands/`, `references/`, `scripts/connectors/`.

Install instructions live in [README.md](README.md). Keep this file focused on authoring and maintenance rules.

## Skill Format Specifications

### Required Frontmatter

| Field | Required | Rules |
|-------|----------|-------|
| `name` | Yes | 1-64 chars, lowercase a-z, numbers, hyphens. Must match directory name. Lowercase slug `^[a-z0-9][a-z0-9-]*$`. |
| `version` | Yes | Semver string. Must match `metadata.version` and the row in `VERSIONS.md`. |
| `description` | Yes | 1-1024 chars. Include: what it does, trigger phrases, scope boundaries. Optimized for `npx skills find`. |

### Repo-Required / Spec-Optional Frontmatter

| Field | Purpose |
|-------|---------|
| `license` | License name (default: Apache-2.0) |
| `compatibility` | Platform list |
| `allowed-tools` | Pre-approved tools (e.g., `WebFetch`) |
| `metadata.author/version/geo-relevance/tags/triggers` | Discovery and categorization. `metadata.version` must match top-level `version`. |
| `when_to_use` | Trigger scenarios for auto-invocation (underscores, not hyphens) |
| `argument-hint` | Argument format hint in command picker |

### Description Best Practices

Start with `Use when the user asks to "..."`, then one sentence on function, then scope boundaries linking related skills.

## Quality Frameworks

See [CLAUDE.md § Quality Frameworks](CLAUDE.md) for details. Summary:
- **CORE-EEAT** (80 items, 8 dimensions): content quality. [Full reference](references/core-eeat-benchmark.md)
- **CITE** (40 items, 4 dimensions): domain authority. [Full reference](references/cite-domain-rating.md)
- Veto items: CORE-EEAT (T04, C01, R10) · CITE (T03, T05, T09)

## Tool Connector Pattern

Skills use `~~category` placeholders. See [CONNECTORS.md](CONNECTORS.md). Every skill works at Tier 1 (no tools). MCP adds Tier 2/3.

## Inter-Skill Handoff

See [CLAUDE.md § Inter-Skill Handoff](CLAUDE.md). Key fields: objective, findings, evidence, open loops, keyword, content type, scores (CORE-EEAT/CITE), priority items, URL.

## Git Workflow

- **Branch naming**: `feature/skill-name`, `fix/skill-name`, `docs/description`
- **Conventional Commits**: `feat:`, `fix:`, `docs:`
- **After skill changes**: update tracking files (VERSIONS.md, `.claude-plugin/plugin.json`, marketplace.json, README.md, CLAUDE.md). For release bumps, also sync localized README badges and marketplace mirrors.
- **Use `references/` for detail** — keep `SKILL.md` focused. Auditor-class skills inline the protocol runbook directly in their `SKILL.md` body.
- **Validate**: `./scripts/validate-skill.sh <category>/<skill-name>` before release PRs.

## Writing Style

- Direct, instructional, second person
- Bold key terms on first use
- Code blocks for commands/templates; tables for structured data
- One skill per file; put extras in `references/`
