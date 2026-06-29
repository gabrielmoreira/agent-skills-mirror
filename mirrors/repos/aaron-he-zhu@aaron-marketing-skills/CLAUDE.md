# Aaron Marketing Skills — Claude Code Context

This plugin provides **38 skills and 5 commands** across two marketing disciplines: Search (SEO/GEO) and influencer marketing (IMPACT). All 38 skills follow one shared contract: trigger, quick start, skill contract, handoff summary, and next best skill. Skills are auto-loaded by context; commands are invoked with `/aaron-marketing:`. Current bundle version: `10.0.1` (see [VERSIONS.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/VERSIONS.md)).

> Umbrella repo, renamed from `seo-geo-claude-skills` (stars/forks/issues/history carried over by the GitHub rename). The SEO/GEO-only product still lives, unchanged, at the original [seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills) URL as a standalone repo.

## Skills by Phase

**Search — SEO/GEO (20):**

| Phase | Skills |
|-------|--------|
| **Research** | `keyword-research`, `competitor-analysis`, `serp-analysis`, `content-gap-analysis` |
| **Build** | `seo-content-writer`, `geo-content-optimizer`, `meta-tags-optimizer`, `schema-markup-generator` |
| **Optimize** | `on-page-seo-auditor`, `technical-seo-checker`, `internal-linking-optimizer`, `content-refresher` |
| **Monitor** | `rank-tracker`, `backlink-analyzer`, `performance-reporter`, `alert-manager` |
| **Cross-cutting / Protocol** | `content-quality-auditor`, `domain-authority-auditor`, `entity-optimizer`, `memory-management` |

**Influencer — IMPACT (18):**

| Phase | Skills |
|-------|--------|
| **Insight** | `audience-analyzer`, `niche-researcher`, `trend-spotter` |
| **Map** | `influencer-discovery`, `fit-scorer`, `competitor-tracker` |
| **Plan** | `campaign-planner`, `brief-generator`, `budget-optimizer` |
| **Activate** | `outreach-manager`, `content-reviewer`, `contract-helper` |
| **Convert** | `content-amplifier`, `ugc-repurposer`, `landing-optimizer` |
| **Track** | `performance-analyzer`, `roi-calculator`, `report-generator` |

## One-Shot Commands

**Five commands**, organized by SEO/GEO intent. Day-to-day work starts with `/aaron-marketing:auto`; the other four are explicit mode entrypoints. Not sure? Use `/aaron-marketing:auto`:

```
/aaron-marketing:auto      — Infer SEO/GEO intent and run the smallest useful workflow (add --deep for exhaustive/stress-test)
/aaron-marketing:research  — Keyword demand, SERP intent, competitors, content gaps, site/topic/entity maps
/aaron-marketing:create    — Brief, write, series, refresh, CMS-neutral publish package (--brief|--series|--refresh|--publish|--meta|--schema)
/aaron-marketing:audit     — On-page + CORE-EEAT quality, technical SEO, AI visibility, domain authority (--full|--tech|--visibility|--authority)
/aaron-marketing:track     — Rankings, alerts, performance reports, project memory (--alert|--report|--remember)
```

## Quality Frameworks

- **CORE-EEAT** ([references/core-eeat-benchmark.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/core-eeat-benchmark.md)): 80-item content quality framework (8 dimensions). GEO Score = CORE avg; SEO Score = EEAT avg. Three veto items: T04, C01, R10.
- **CITE** ([references/cite-domain-rating.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/cite-domain-rating.md)): 40-item domain authority framework (4 dimensions). Three veto items: T03, T05, T09.
- **C³** ([references/c3-benchmark.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/c3-benchmark.md)): influencer marketing framework — Creator/Content/Campaign scored on ACE/ART/ROI (9 dimensions). Veto items: ACE A2/C1/E2, ART T1/T2. CVI = (ACE×ART×ROI)^(1/3).

## Operating Contract

- Shared contract reference: [references/skill-contract.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/skill-contract.md)
- Shared state model: [references/state-model.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/state-model.md)
- Protocol roles:
  - `content-quality-auditor` = publish readiness gate
  - `domain-authority-auditor` = citation trust gate
  - `entity-optimizer` = canonical entity profile
  - `memory-management` = campaign memory loop
- Hook automation: `hooks/hooks.json` — command-backed hooks for SessionStart (startup/resume/clear/compact: injects sanitized hot-cache + an open-loops pointer), UserPromptSubmit, PostToolUse (hot-cache size warning + auditor Artifact Gate), and a Stop hook that is a no-op (exits silently)
- Temperature memory: HOT (`memory/hot-cache.md`, 80 lines, auto-loaded) / WARM (`memory/` subdirs) / COLD (`memory/archive/`)
- Dual truncation: HOT tier limited to 80 lines AND 25KB (whichever triggers first)

## Inter-Skill Handoff

When a skill recommends running another, pass: objective, key findings/output, evidence, open loops, target keyword, content type, completion status (DONE/DONE_WITH_CONCERNS/BLOCKED/NEEDS_INPUT), CORE-EEAT dimension scores (e.g., `C:75 O:60 R:80 E:45`), CITE scores, priority item IDs, and content URL.

If `memory-management` is active, prior audit results load automatically from the hot cache.

## Tool Connector Pattern

Skills use `~~category` placeholders (e.g., `~~SEO tool`, `~~analytics`). Every skill works without any integrations (Tier 1). [CONNECTORS.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/CONNECTORS.md) documents a verified **free/keyless data recipe for each category** — Google Search Console & GA4 (own data), PageSpeed/CrUX, Wikidata SPARQL, Common Crawl, Wayback CDX, Open PageRank, advertools — so skills can pull real data with zero paid-tool dependency. MCP servers catalogued in `.mcp.json` (Ahrefs, Semrush, SE Ranking, SISTRIX, SimilarWeb, the self-hosted free **OpenSEO** suite, Cloudflare, Vercel, HubSpot, Amplitude, Notion, Webflow, Sanity, Contentful, Slack) are an **opt-in** Tier 2/3 automation layer — `plugin.json` no longer auto-registers them, so installing the plugin adds nothing to the user's `/mcp` list; users copy the entries they want into their own MCP config.

## Contribution Rules

- All `SKILL.md` files must include: `name`, `version`, `description`, `license`, `compatibility`, `metadata` frontmatter. Recommended: `when_to_use` (underscores, not hyphens) and `argument-hint`.
- `plugin.json` must include: `id` and `description` at top level. Commands are auto-discovered from `./commands/`; skills are listed as directory paths.
- Keep each `SKILL.md` focused — move long detail into `references/` subdirectories. The protocol-layer auditor skills (`content-quality-auditor`, `domain-authority-auditor`) `Read references/auditor-runbook.md` at activation (the framework-agnostic SSOT: handoff schema, cap method, Artifact Gate, translation format) via a plugin-relative path, and keep only their **framework-specific** §2 worked examples, §3 guardrails, and §5 veto-ID rows inline (CORE-EEAT vs CITE diverge and must not be byte-identical). All intra-repo links in `SKILL.md`/`references/` are plugin-relative paths, never `blob/main` GitHub URLs — the validator enforces this.
- High-volume `references/` packs should prefer compact starter templates, step matrices, and checklists over long worked outlines. Keep canonical examples only where they materially improve execution quality.
- After updating a skill, keep the tracking files in step — the **authoritative 8-file list** lives in [CONTRIBUTING.md §6](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/CONTRIBUTING.md) (`VERSIONS.md`, `.claude-plugin/plugin.json`, the root `marketplace.json` and its `.claude-plugin/marketplace.json` mirror, `README.md`, this `CLAUDE.md`, `AGENTS.md`, and `docs/README.zh.md`).
- Design philosophy: skills are content (Markdown). Allowed code: the bash validator (`scripts/validate-skill.sh`) and **zero-dependency Python-stdlib connector helpers** under `scripts/connectors/` that pull public/own data locally so skills don't need external tools (see [CONNECTORS.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/CONNECTORS.md)). No third-party / `pip` dependencies.
- Keep the shared contract and state-model language consistent with `references/skill-contract.md` and `references/state-model.md`.
- Branch naming: `feature/skill-name`, `fix/skill-name`, `docs/description`

## CLI Tools

System PATH in Claude Code sessions is minimal (`/usr/bin:/bin:/usr/sbin:/sbin`). Tools installed via Homebrew or npm are NOT on PATH by default. Always use absolute paths:

- **gh** (GitHub CLI): `/opt/homebrew/bin/gh`
- **node**: `/usr/local/bin/node`
- **bun**: `~/.bun/bin/bun`

Or prepend PATH at start of command: `export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"; gh ...`

### GitHub Release

```bash
/opt/homebrew/bin/gh release create vX.Y.Z --title "title" --notes "body"
```

> [AGENTS.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/AGENTS.md) · [README.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/README.md)
