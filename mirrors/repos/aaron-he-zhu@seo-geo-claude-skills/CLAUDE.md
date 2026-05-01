# SEO & GEO Skills Library — Claude Code Context

This plugin provides **20 skills and 17 commands** for Search Engine Optimization (SEO) and Generative Engine Optimization (GEO). All 20 skills follow one shared contract: trigger, quick start, skill contract, handoff summary, and next best skill. Skills are auto-loaded by context; commands are invoked with `/seo:`. Current bundle version: `9.9.5` (see [VERSIONS.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/VERSIONS.md)).

## Skills by Phase

| Phase | Skills |
|-------|--------|
| **Research** | `keyword-research`, `competitor-analysis`, `serp-analysis`, `content-gap-analysis` |
| **Build** | `seo-content-writer`, `geo-content-optimizer`, `meta-tags-optimizer`, `schema-markup-generator` |
| **Optimize** | `on-page-seo-auditor`, `technical-seo-checker`, `internal-linking-optimizer`, `content-refresher` |
| **Monitor** | `rank-tracker`, `backlink-analyzer`, `performance-reporter`, `alert-manager` |
| **Cross-cutting / Protocol** | `content-quality-auditor`, `domain-authority-auditor`, `entity-optimizer`, `memory-management` |

## One-Shot Commands

**User commands (10)** — day-to-day SEO/GEO work:

```
/seo:audit-page      — On-page SEO + CORE-EEAT audit
/seo:audit-domain    — CITE domain authority audit
/seo:check-technical — Technical SEO health check
/seo:write-content   — SEO + GEO optimized content
/seo:keyword-research — Keyword discovery and clustering
/seo:optimize-meta   — Title tags and meta descriptions
/seo:generate-schema — JSON-LD structured data
/seo:report          — Performance report
/seo:setup-alert     — Monitoring alert configuration
/seo:geo-drift-check — (experimental, v9.0+) Validate GEO Score against actual AI-engine citations
```

**Maintenance commands (7)** — for library maintainers / power users. Safe to ignore for daily use:

```
/seo:wiki-lint          — Wiki health check: contradictions, orphans, stale claims
/seo:contract-lint      — Auditor Runbook drift detection, handoff schema check, jargon leak scan (v7.1.0+)
/seo:run-evals          — Run lightweight skill eval cases and emit validation_results for evolution review
/seo:sync-versions      — Propagate canonical version from .claude-plugin/plugin.json to all cross-agent manifests (v9.0+, replaces scripts/sync-versions.py)
/seo:validate-library   — Library-level quality gate: description budgets, YAML field order, language coverage, duplicate triggers, release guardrails (v9.0+, replaces scripts/validate-descriptions.py)
/seo:evolve-skill       — Generate evidence-backed skill evolution proposals; proposal-only, no edits
/seo:skillify           — Audit proposed or changed skills for completeness, routing, eval coverage, and release impact; proposal-only, no edits
```

## Quality Frameworks

- **CORE-EEAT** ([references/core-eeat-benchmark.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/core-eeat-benchmark.md)): 80-item content quality framework (8 dimensions). GEO Score = CORE avg; SEO Score = EEAT avg. Three veto items: T04, C01, R10.
- **CITE** ([references/cite-domain-rating.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/cite-domain-rating.md)): 40-item domain authority framework (4 dimensions). Three veto items: T03, T05, T09.

## Operating Contract

- Shared contract reference: [references/skill-contract.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md)
- Shared state model: [references/state-model.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/state-model.md)
- Protocol roles:
  - `content-quality-auditor` = publish readiness gate
  - `domain-authority-auditor` = citation trust gate
  - `entity-optimizer` = canonical entity profile
  - `memory-management` = campaign memory loop
- Hook automation: `hooks/hooks.json` — prompt-based hooks for SessionStart, UserPromptSubmit, PostToolUse, and a guarded allow-only Stop check
- Temperature memory: HOT (`memory/hot-cache.md`, 80 lines, auto-loaded) / WARM (`memory/` subdirs) / COLD (`memory/archive/`)
- Wiki compilation view: `memory/wiki/` — auto-refreshed structured index of WARM files with project isolation, 健康度 scoring, and user-tier guidance. Delete `memory/wiki/` to revert. Design history is archived in [proposal-wiki-layer-v3.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/proposal-wiki-layer-v3.md); active behavior lives in `state-model.md`, `memory-management`, and `hooks/hooks.json`.
- Dual truncation: HOT tier limited to 80 lines AND 25KB (whichever triggers first)

## Inter-Skill Handoff

When a skill recommends running another, pass: objective, key findings/output, evidence, open loops, target keyword, content type, completion status (DONE/DONE_WITH_CONCERNS/BLOCKED/NEEDS_INPUT), CORE-EEAT dimension scores (e.g., `C:75 O:60 R:80 E:45`), CITE scores, priority item IDs, and content URL.

If `memory-management` is active, prior audit results load automatically from the hot cache in this [CLAUDE.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CLAUDE.md) file.

## Tool Connector Pattern

Skills use `~~category` placeholders (e.g., `~~SEO tool`, `~~analytics`). Every skill works without any integrations (Tier 1). MCP servers in `.mcp.json` add Ahrefs, Semrush, SE Ranking, SISTRIX, SimilarWeb, Cloudflare, Vercel, HubSpot, Amplitude, Notion, Webflow, Sanity, Contentful, Slack.

## Contribution Rules

- All `SKILL.md` files must include: `name`, `version`, `description`, `license`, `compatibility`, `metadata` frontmatter. Recommended: `when_to_use` (underscores, not hyphens) and `argument-hint`.
- `plugin.json` must include: `id` and `description` at top level. Commands auto-discovered from `./commands/` directory; skills listed as directory paths
- Keep `SKILL.md` body under 350 lines — move detail to `references/` subdirectories. **Exception**: protocol-layer auditor skills (currently `content-quality-auditor` and `domain-authority-auditor`) may inline the authoritative Auditor Runbook §1-5 (~270 lines) directly in their SKILL.md body, bringing them to a ~750 line ceiling. Inlining is required because markdown-linked references do not execute reliably at skill activation. The inline block is delimited by `<!-- runbook-sync start: source_sha256=... block_sha256=... -->` markers and validated by `/seo:contract-lint`. See [references/decisions/2026-04-adr-001-inline-auditor-runbook.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/decisions/2026-04-adr-001-inline-auditor-runbook.md).
- High-volume `references/` packs should prefer compact starter templates, step matrices, and checklists over long worked outlines. Keep canonical examples only where they materially improve execution quality.
- **New auditor-class skill authors**: start with [references/AUDITOR-AUTHORS.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/AUDITOR-AUTHORS.md) — template skeleton, veto registration checklist, anti-patterns, and sync procedure.
- After updating a skill: update all 5 tracking files — `VERSIONS.md`, `.claude-plugin/plugin.json`, `marketplace.json` (repo root), `README.md` skills table, and this `CLAUDE.md` category table. The root `marketplace.json` is mirrored to `.claude-plugin/marketplace.json` (both must be byte-identical — see [#8](https://github.com/aaron-he-zhu/seo-geo-claude-skills/issues/8) for why they can't be a symlink). The CI script `.github/scripts/sync-skills.js` keeps them in sync automatically, but manual edits to the root require `cp marketplace.json .claude-plugin/marketplace.json` afterward. `/seo:validate-library` check #6 catches drift.
- Version bump also syncs 3 cross-agent manifests — `gemini-extension.json`, `qwen-extension.json`, `.codebuddy-plugin/marketplace.json`. Run `/seo:sync-versions` after editing `.claude-plugin/plugin.json` to propagate the version automatically, then run `bash scripts/validate-slimming-guardrails.sh` to catch release-surface drift that sync alone cannot prove (CITATION, badges, marketplace mirror, must-keep aliases, and template regressions). A jq one-liner fallback for CI / no-Claude environments is documented in [commands/sync-versions.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/commands/sync-versions.md).
- Design philosophy: the repo is content-only — no `.py` scripts. Developer utilities are either bash (`scripts/validate-skill.sh`) or pure-markdown slash commands. If a new utility is needed, add it as a `commands/*.md` file and mark it a maintenance command.
- Keep the shared contract and state-model language consistent with `references/skill-contract.md` and `references/state-model.md`
- Branch naming: `feature/skill-name`, `fix/skill-name`, `docs/description`

## CLI Tools

System PATH in Claude Code sessions is minimal (`/usr/bin:/bin:/usr/sbin:/sbin`). Tools installed via Homebrew or npm are NOT on PATH by default. Always use absolute paths:

- **gh** (GitHub CLI): `/opt/homebrew/bin/gh`
- **clawhub** (ClawHub CLI): `/usr/local/bin/clawhub` (requires node at `/usr/local/bin/node`)
- **node**: `/usr/local/bin/node`
- **bun**: `~/.bun/bin/bun`

Or prepend PATH at start of command: `export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"; gh ...`

### ClawHub Publishing

Skills are published **individually** (not as a single plugin package). Each `<category>/<slug>/SKILL.md` is a separate ClawHub skill.

```bash
# Auth check
/usr/local/bin/clawhub whoami

# Publish one skill
/usr/local/bin/clawhub publish <category>/<slug> --version X.Y.Z --changelog "text" --tags latest --no-input

# Publish all discovered skills (batch)
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"
find research build optimize monitor cross-cutting -mindepth 2 -maxdepth 2 -name SKILL.md -print | sort | while read -r file; do
  dir="$(dirname "$file")"
  clawhub publish "$dir" --version X.Y.Z --changelog "text" --tags latest --no-input
done
```

### GitHub Release

```bash
/opt/homebrew/bin/gh release create vX.Y.Z --title "title" --notes "body"
```

> [AGENTS.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/AGENTS.md) · [README.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/README.md) · Install: [ClawHub](https://clawhub.ai/u/aaron-he-zhu) · [skills.sh](https://skills.sh/aaron-he-zhu/seo-geo-claude-skills)
