# Aaron Marketing Skills — Claude Code Context

This plugin provides **54 skills and 4 commands** across three marketing disciplines — SEO/GEO, influencer marketing (IMPACT), and Paid Ads (ROAS) — plus a shared protocol layer. All 54 skills follow one shared contract: trigger, quick start, skill contract, handoff summary, and next best skill. Skills are auto-loaded by context; commands are invoked with `/aaron-marketing:`. Current bundle version: `11.0.0` (see [VERSIONS.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/VERSIONS.md)).

> Umbrella repo, renamed from `seo-geo-claude-skills` (stars/forks/issues/history carried over by the GitHub rename). The SEO/GEO-only product still lives, unchanged, at the original [seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills) URL as a standalone repo.

## Skills by Phase

The three disciplines share one **meta-lifecycle** spine (an approximate bridge — each adapts the granularity to its own workflow, so phase *counts* and exact semantics differ by design):

| Meta-stage | SEO/GEO | Influencer (IMPACT) | Paid (ROAS) |
|------------|---------|---------------------|-------------|
| **Understand** | research | insight, map | Research |
| **Plan / create** | build | plan | Orchestrate |
| **Activate / optimize** | optimize | activate, convert | Activate |
| **Measure** | monitor | track | Scale |
| **Cross-cutting** | the **protocol layer** (entity/creator/claims truth registries · memory) serves all three; the 4 auditor-class gates live in their disciplines | | |

Notes: "Activate" means creator outreach in IMPACT but account-gating in ROAS — same word, discipline-specific scope. All three disciplines use phase *directories* — paid skills live under `paid/<phase>/` (research/orchestrate/activate/scale).

**SEO/GEO (24):**

| Phase | Skills |
|-------|--------|
| **Research** | `keyword-research`, `competitor-analysis`, `serp-analysis`, `content-gap-analysis` |
| **Build** | `seo-content-writer`, `geo-content-optimizer`, `meta-tags-optimizer`, `schema-markup-generator`, `programmatic-seo`, `parasite-seo`, `comparison-page-builder`, `local-seo` |
| **Optimize** | `on-page-seo-auditor`, `technical-seo-checker`, `internal-linking-optimizer`, `content-refresher`, `site-architecture`, `content-quality-auditor` |
| **Monitor** | `rank-tracker`, `backlink-analyzer`, `performance-reporter`, `alert-manager`, `ai-traffic`, `domain-authority-auditor` |

**Protocol layer — cross-cutting (4):** shared truth & memory machinery outside the discipline phase-flows — 3 discipline-anchored truth registries (`entity-optimizer` → SEO/GEO, `creator-registry` → influencer, `offer-claims-registry` → paid) plus the cross-discipline `memory-management`. Counted separately. The auditor-class **gate role** spans 4 skills, all discipline-resident and counted there: `content-quality-auditor` (optimize/), `domain-authority-auditor` (monitor/), `content-reviewer` (activate/), `ad-account-auditor` (paid/activate/).

| Group | Skills |
|-------|--------|
| **Protocol** | `entity-optimizer`, `creator-registry`, `offer-claims-registry`, `memory-management` |

**Influencer — IMPACT (18):**

| Phase | Skills |
|-------|--------|
| **Insight** | `audience-analyzer`, `niche-researcher`, `trend-spotter` |
| **Map** | `influencer-discovery`, `fit-scorer`, `competitor-tracker` |
| **Plan** | `campaign-planner`, `brief-generator`, `budget-optimizer` |
| **Activate** | `outreach-manager`, `content-reviewer`, `contract-helper` |
| **Convert** | `content-amplifier`, `ugc-repurposer`, `landing-optimizer` |
| **Track** | `performance-analyzer`, `roi-calculator`, `report-generator` |

**Paid Ads — ROAS (8):** phase directories under `paid/` follow the ROAS loop (Research → Orchestrate → Activate → Scale).

| Phase | Skills |
|-------|--------|
| **Research** | `campaign-architect` (structure + search-term-mining mode), `audience-segment-builder` |
| **Orchestrate** | `ad-creative-builder`, `ad-test-designer` |
| **Activate** | `ad-account-auditor` (RQS gate + launch go/no-go mode), `conversion-signal-qa` |
| **Scale** | `paid-measurement-loop`, `attribution-reconciler` |

Reused cross-discipline (counted in the phases, not duplicated): `budget-optimizer` (spend allocation + bid-pacing/learning-phase mode), `landing-optimizer` (post-click), `roi-calculator` (return math), `report-generator`, `performance-analyzer`.

## One-Shot Commands

**Four commands.** `/aaron-marketing:auto` infers intent across all disciplines; each discipline has one explicit entrypoint. Not sure? Use `/aaron-marketing:auto`:

```
/aaron-marketing:auto      — Infer marketing intent across all disciplines and run the smallest useful workflow (add --deep for exhaustive/stress-test)
/aaron-marketing:seo-geo   — SEO/GEO end-to-end (--mode research|create|audit|track; per-mode flags preserved: --brief/--series/--refresh/--publish/--meta/--schema/--type, --full/--tech/--visibility/--authority, --alert/--report/--remember/--period, --competitors/--map)
/aaron-marketing:impact    — Influencer (IMPACT): insight / map / plan / activate / convert / track (--phase to force a stage)
/aaron-marketing:paid      — Paid ads (ROAS loop): research / orchestrate / activate / scale (--phase to force a stage)
```

## Quality Frameworks

- **CORE-EEAT** ([references/core-eeat-benchmark.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/core-eeat-benchmark.md)): 80-item content quality framework (8 dimensions). GEO Score = CORE avg; SEO Score = EEAT avg. Three veto items: T04, C01, R10.
- **CITE** ([references/cite-domain-rating.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/cite-domain-rating.md)): 40-item domain authority framework (4 dimensions). Three veto items: T03, T05, T09.
- **C³** ([references/c3-benchmark.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/c3-benchmark.md)): influencer marketing framework — Creator/Content/Campaign scored on ACE/ART/ROI (9 dimensions). Veto items: ACE A2/C1/E2, ART T1/T2. CVI = (ACE×ART×ROI)^(1/3).
- **ROAS** ([references/roas-benchmark.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/roas-benchmark.md)): paid ads framework — R (Return), O (Offer), A (Audience), S (Spend-efficiency). RQS = arithmetic weighted-mean rollup (like CITE). Veto items: R1/R2/O1/O2/A1.

## Operating Contract

- Shared contract reference: [references/skill-contract.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/skill-contract.md)
- Shared state model: [references/state-model.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/state-model.md)
- Protocol roles (role assignments — the `protocol/` directory itself is 4 skills; the 4 gates live in their home disciplines; `content-reviewer`/`ad-account-auditor` play gate roles but are counted under their home disciplines):
  - `content-quality-auditor` = publish readiness gate
  - `domain-authority-auditor` = citation trust gate
  - `content-reviewer` = C³ ART gate
  - `ad-account-auditor` = ROAS gate
  - `entity-optimizer` = canonical entity profile
  - `creator-registry` = canonical creator roster/dossier (influencer truth SSOT)
  - `offer-claims-registry` = offer & claim-substantiation record (paid truth SSOT)
  - `memory-management` = campaign memory loop
- Hook automation: `hooks/hooks.json` — command-backed hooks for SessionStart (startup/resume/clear/compact: injects sanitized hot-cache + an open-loops pointer), UserPromptSubmit, PostToolUse (hot-cache size warning + auditor Artifact Gate), and a Stop hook that is a no-op (exits silently)
- Temperature memory: HOT (`memory/hot-cache.md`, 80 lines, auto-loaded) / WARM (`memory/` subdirs) / COLD (`memory/archive/`)
- Dual truncation: HOT tier limited to 80 lines AND 25KB (whichever triggers first)

## Inter-Skill Handoff

When a skill recommends running another, pass the standard shape from `references/skill-contract.md` §Handoff Summary Format: status (DONE/DONE_WITH_CONCERNS/BLOCKED/NEEDS_INPUT), objective, key findings/output, evidence (each labeled Measured/User-provided/Estimated), assumptions, open loops, and the recommended next skill. The 4 auditor-class gates additionally emit `cap_applied`, `raw_overall_score`, and `final_overall_score` per `references/auditor-runbook.md` §1.

If `memory-management` is active, prior audit results load automatically from the hot cache.

## Tool Connector Pattern

Skills use `~~category` placeholders (e.g., `~~SEO tool`, `~~analytics`). Every skill works without any integrations (Tier 1). [CONNECTORS.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/CONNECTORS.md) documents a verified **free/keyless data recipe for each category** — Google Search Console & GA4 (own data), PageSpeed/CrUX, Wikidata SPARQL, Common Crawl, Wayback CDX, Open PageRank, advertools — so skills can pull real data with zero paid-tool dependency. MCP servers catalogued in `docs/mcp-catalog.json` (Ahrefs, Semrush, SE Ranking, SISTRIX, SimilarWeb, the self-hosted free **OpenSEO** suite, Cloudflare, Vercel, HubSpot, Amplitude, Notion, Webflow, Sanity, Contentful, Slack) are an **opt-in** Tier 2/3 automation layer — the catalog is kept outside the plugin-root `.mcp.json` path that Claude Code auto-registers (and `plugin.json` carries no `mcpServers` key), so installing the plugin adds nothing to the user's `/mcp` list; users copy the entries they want into their own MCP config.

## Contribution Rules

- All `SKILL.md` files must include: `name`, `version`, `description`, `license`, `compatibility`, `metadata` frontmatter. Recommended: `when_to_use` (underscores, not hyphens) and `argument-hint`.
- `plugin.json` must include: `name` (the spec-required identifier) and `description` at top level, plus `id` (the marketplace identity key downstream tooling references). Commands are auto-discovered from `./commands/`; skills are listed as directory paths.
- Keep each `SKILL.md` focused — move long detail into `references/` subdirectories. The four auditor-class gate skills (`content-quality-auditor`, `domain-authority-auditor`, `content-reviewer`, `ad-account-auditor` — discipline-resident, not protocol-layer) `Read references/auditor-runbook.md` at activation (the framework-agnostic SSOT: handoff schema, cap method, Artifact Gate, translation format) via a plugin-relative path, and keep only their **framework-specific** §2 worked examples, §3 guardrails, and §5 veto-ID rows inline (CORE-EEAT / CITE / C³ ART / ROAS diverge and must not be byte-identical). All intra-repo links in `SKILL.md`/`references/` are plugin-relative paths, never `blob/main` GitHub URLs — the validator enforces this.
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
