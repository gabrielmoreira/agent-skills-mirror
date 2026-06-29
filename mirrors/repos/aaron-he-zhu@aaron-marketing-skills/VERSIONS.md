# Aaron Marketing Skills — Versions

Current versions for the plugin and all 38 skills. Agents can fetch this file from `https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/VERSIONS.md` once per session.

**Current release**: `10.0.1` (2026-06-28). Skill `version`, `metadata.version`, plugin manifests, marketplace files, and badges are aligned to the same public version.

## Skills

| Skill | Category | Version | Last Updated |
|-------|----------|---------|--------------|
| keyword-research | research | 10.0.1 | 2026-06-28 |
| competitor-analysis | research | 10.0.1 | 2026-06-28 |
| serp-analysis | research | 10.0.1 | 2026-06-28 |
| content-gap-analysis | research | 10.0.1 | 2026-06-28 |
| seo-content-writer | build | 10.0.1 | 2026-06-28 |
| geo-content-optimizer | build | 10.0.1 | 2026-06-28 |
| meta-tags-optimizer | build | 10.0.1 | 2026-06-28 |
| schema-markup-generator | build | 10.0.1 | 2026-06-28 |
| on-page-seo-auditor | optimize | 10.0.1 | 2026-06-28 |
| technical-seo-checker | optimize | 10.0.1 | 2026-06-28 |
| internal-linking-optimizer | optimize | 10.0.1 | 2026-06-28 |
| content-refresher | optimize | 10.0.1 | 2026-06-28 |
| rank-tracker | monitor | 10.0.1 | 2026-06-28 |
| backlink-analyzer | monitor | 10.0.1 | 2026-06-28 |
| performance-reporter | monitor | 10.0.1 | 2026-06-28 |
| alert-manager | monitor | 10.0.1 | 2026-06-28 |
| content-quality-auditor | cross-cutting | 10.0.1 | 2026-06-28 |
| domain-authority-auditor | cross-cutting | 10.0.1 | 2026-06-28 |
| entity-optimizer | cross-cutting | 10.0.1 | 2026-06-28 |
| memory-management | cross-cutting | 10.0.1 | 2026-06-28 |
| audience-analyzer | insight | 10.0.1 | 2026-06-28 |
| niche-researcher | insight | 10.0.1 | 2026-06-28 |
| trend-spotter | insight | 10.0.1 | 2026-06-28 |
| influencer-discovery | map | 10.0.1 | 2026-06-28 |
| fit-scorer | map | 10.0.1 | 2026-06-28 |
| competitor-tracker | map | 10.0.1 | 2026-06-28 |
| campaign-planner | plan | 10.0.1 | 2026-06-28 |
| brief-generator | plan | 10.0.1 | 2026-06-28 |
| budget-optimizer | plan | 10.0.1 | 2026-06-28 |
| outreach-manager | activate | 10.0.1 | 2026-06-28 |
| content-reviewer | activate | 10.0.1 | 2026-06-28 |
| contract-helper | activate | 10.0.1 | 2026-06-28 |
| content-amplifier | convert | 10.0.1 | 2026-06-28 |
| ugc-repurposer | convert | 10.0.1 | 2026-06-28 |
| landing-optimizer | convert | 10.0.1 | 2026-06-28 |
| performance-analyzer | track | 10.0.1 | 2026-06-28 |
| roi-calculator | track | 10.0.1 | 2026-06-28 |
| report-generator | track | 10.0.1 | 2026-06-28 |

## Changelog

### v10.0.1 — Quality & correctness patch: Artifact Gate fix, C³ wiring, full-coverage CI (2026-06-28)

**Fixed**
- Artifact Gate: the PostToolUse hook's `hb()` body parser truncated auditor artifacts at the first blank line, false-blocking every compliant `memory/audits/` output; it now reads the full post-frontmatter body. Reconciled the `auditor-runbook.md` cap-field prose with the authoritative §2/§4 (only `final_overall_score` is BLOCKED-exempt).
- Connectors: `_http.get` no longer sleeps after the final retry; `crawl.py` re-bases the same-host filter onto the landing host after an apex→www redirect.

**Changed**
- C³ now enforced (route C): `fit-scorer` emits ACE with the A2/C1/E2 veto and caps the score on veto; `content-reviewer` enforces ART T1 (FTC disclosure) / T2 (claim integrity) as Reject vetoes; `roi-calculator` emits the CVI rollup. `c3-benchmark.md` "Where it is used" corrected so `influencer-discovery`/`performance-analyzer` inform/contribute rather than compute.
- Shared contract + state model extended to all 38 skills: Influencer category defaults, the `memory/influencer/<skill>/` write path, and C³ cross-links.

**Added**
- CI validates all 38 skills (was 20) and runs new hook-gate + connector unit tests (connector tests 3 → 11).
- `CONNECTORS.md` recipes for the 18 influencer `~~` categories; unified 8-file tracking list (authoritative in `CONTRIBUTING.md`); eval seed cases for all 18 influencer skills (evals now cover 38/38); `bug-report.yml` issue template; `memory/{research,content,monitoring,archive}/` scaffolding; validator eval-presence advisory.

**Versions**: all 38 skills, plugin manifests, and marketplace mirrors unified at `10.0.1`.

### v10.0.0 — Marketing umbrella: SEO/GEO + influencer-marketing merge + rename (2026-06-28)

**Repository rename**: `seo-geo-claude-skills` → `aaron-marketing-skills`. The GitHub rename carries stars, forks, issues, and full history to the new name. The SEO/GEO-only product continues to live, unchanged, at the original `seo-geo-claude-skills` URL as a standalone repo (fresh star count).

**Merge** — four projects consolidated into one library:
- `influencer-marketing-agent-skills` → **18 new skills** on the IMPACT framework (Insight · Map · Plan · Activate · Convert · Track), normalized to the shared skill contract (full frontmatter + Quick Start, Skill Contract, Handoff Summary, Data Sources, Instructions, Reference Materials, Next Best Skill).
- `influencer-marketing-c3-benchmark` → the **C³** framework (Creator/Content/Campaign on ACE/ART/ROI) at `references/c3-benchmark.md` and `references/c3/`.
- `core-eeat-content-benchmark` and `cite-domain-rating` → CORE-EEAT and CITE retained as canonical references (already embedded).

**Bundle**: now **38 skills + 5 commands** (was 20 + 5). Three frameworks: CORE-EEAT (content), CITE (domain), C³ (influencer).

**Command namespace**: `/aaron-seo-geo:*` → `/aaron-marketing:*` (marketplace plugin id is now `aaron-marketing`). Old `/seo:*` and `/aaron-seo-geo:*` invocations recover via `/aaron-marketing:auto`.

**Versions**: all 38 skills, plugin manifests, and marketplace mirrors unified at `10.0.0`.

### v9.9.11 — URL-stable overhaul + open-seo connector borrows (2026-06-28)

Ships the `refactor/url-stable-overhaul` line as a single release. The 20 skill directories, `name`, and `description` stay frozen (existing GitHub URLs unchanged); everything inside the skill bodies and the supporting layers was reworked.

**URL-stable overhaul**:
- All intra-repo links in `SKILL.md`/`references/` are plugin-relative paths; `validate-skill.sh` now fails on any `blob/main` GitHub URL. Connector invocations use `${CLAUDE_PLUGIN_ROOT}/scripts/connectors/...`.
- `references/auditor-runbook.md` is the framework-agnostic SSOT both auditors `Read` at activation; each inlines only its framework-specific CORE-EEAT (8-dim weighted) vs CITE (`C×.35+I×.20+T×.25+E×.20`) examples and veto rows. `raw_overall_score` = weighted total (floor-rounded, pre-cap).
- MCP stays opt-in (`plugin.json` carries no `mcpServers` key; `.mcp.json` is a copy-paste catalog). New `_http.get` scheme allowlist (`http`/`https`) guards sitemap-harvested URLs (LFI/SSRF); `crawl.py` uses `robots.py` for correct Allow/wildcard/UA handling.
- Honesty-bound memory model: explicit-pin + `last_updated` only, no frequency-based promotion; SessionStart surfaces an open-loops pointer.
- New `scripts/connectors/ledger.py` (local JSONL time-series) and `scripts/golden-auditor-math.py` (CI-wired weight-table guard); ledger wired into rank-tracker / performance-reporter / technical-seo-checker. `evals/product-api-scenarios.md` → `references/auto-routing-scenarios.md`.

**Connector borrows** (adapted from [every-app/open-seo](https://github.com/every-app/open-seo)):
- `keyword-research` gains a Search Console **striking-distance** shortcut — mine own GSC queries ranking ~5–20 before broad discovery (API sorts by clicks, no position filter → high `rowLimit` + client-side window), treated as Measured.
- `CONNECTORS.md` adds a subscription-vs-pay-as-you-go **cost model** column and **OpenSEO** as an opt-in, self-hosted, free pay-as-you-go MCP (servers `14 → 15` in `.mcp.json`, still nothing auto-registered).

### v9.9.10 — focus on skills: scaffolding cleanup, 5 commands, quality pass, bundled connectors (2026-06-05)

Removed non-user-facing maintenance and process scaffolding, and consolidated the command surface, so the library focuses on the skills themselves. **Breaking**: the command set is reduced to **5** (`/aaron-marketing:auto`, `/aaron-marketing:research`, `/aaron-marketing:create`, `/aaron-marketing:audit`, `/aaron-marketing:track`) — the bundle is now **20 skills + 5 commands**.

**Removed**:
- Controlled-evolution protocol (`/aaron-marketing:evolve`, EvolutionEvent, `evolution-*` references, `memory/evolution/`) and the GEO-drift feedback loop it fed: the `memory/geo-feedback/` records and the `/aaron-marketing:watch --geo-drift` mode are removed; rankings and alerts now live under `/aaron-marketing:track` only.
- Wiki memory-compilation layer (Phase 1–3, 健康度 scoring, wiki-driven WARM→COLD retirement, `wiki-runbook.md`, recovery/rollback scripts). Plain HOT/WARM/COLD memory and `memory/archive/` are unchanged.
- Maintainer commands `/aaron-marketing:guard` and `/aaron-marketing:skillify`; line-budget / "slimming" ceremony (350-line ceiling, `validate-slimming-guardrails.sh`, the `references/decisions/` ADRs); and the inline-runbook sha256 sync ceremony (the auditor runbook stays inlined — only the hash-drift check is gone).
- Per-vendor distribution catering: `gemini-extension.json`, `qwen-extension.json`, `openclaw.plugin.json`, `.codebuddy-plugin/`, `marketplaces/`, the `distribution/` platform registry, and the ClawHub/OpenClaw publishing workflows. Distribution is now generic: one root `marketplace.json` plus its `.claude-plugin/` mirror.
- Historical design proposals under `.docs/` and `references/proposal-*`.
- `CITATION.cff` (citation-metadata ceremony) and `references/skill-resolver.md` (a derived routing index redundant with the skills' own descriptions) — neither referenced by any skill or command.

**Command re-architecture (20 → 5)**: the 17 user commands plus `/aaron-marketing:max` collapsed into 5 intent commands — `discover`/`compete`/`map` → `/aaron-marketing:research`; `brief`/`write`/`series`/`refresh`/`publish` → `/aaron-marketing:create`; `tech`/`visibility`/`authority` → `/aaron-marketing:audit`; `watch`/`report`/`remember` → `/aaron-marketing:track`; `max` → `/aaron-marketing:auto --deep` (mode flags preserved, e.g. `--meta`, `--schema`, `--alert`, `--report`). Old `/seo:*` and prior command names still recover via `/aaron-marketing:auto`.

**Authoring-quality pass**: a senior-review pass across all 20 skills — narrower `description` triggers, explicit scope boundaries ("not for X — use Y"), verifiable `Done when` criteria, Decision Gates (stop-vs-continue), and a uniform Measured / User-provided / Estimated data-honesty rule so no skill presents an estimate as a fact.

**Bundled zero-dependency connectors**: `scripts/connectors/` adds Python-stdlib-only helpers (no pip) that pull public or own data locally — crawl, on-page, robots/sitemap, link-graph PageRank, PageSpeed/CrUX, schema lint, Wikidata/Knowledge-Graph reconcile, Wayback, Open PageRank, Google Suggest, RSS. Six skills point to a matching helper in their Data Sources; all still run tool-free at Tier 1. Fetched content is treated as data, never instructions.

**Kept**: all 20 skills, the CORE-EEAT and CITE frameworks, the `evals/` quality cases, `scripts/validate-skill.sh`, and HOT/WARM/COLD project memory.

### v9.9.9 — Consolidated 9.x final (2026-05-14)

Final 9.x release consolidating the entire post-v9.0.0 development line into a single coherent shipment. Previous interim tags (v9.5.0, v9.9.0, v9.9.5) and the entire v10.x exploratory line have been retired and folded into this release. Anyone tracking the 9.x line should upgrade directly from v9.0.0 to v9.9.9.

**Added**:
- **Aaron command architecture**: public command API renamed from `/seo:*` to `/aaron-marketing:*`; 17 user commands. New commands: `/aaron-marketing:auto`, `/aaron-marketing:max`, `/aaron-marketing:discover`, `/aaron-marketing:compete`, `/aaron-marketing:map`, `/aaron-marketing:brief`, `/aaron-marketing:series`, `/aaron-marketing:refresh`, `/aaron-marketing:publish`, `/aaron-marketing:visibility`, `/aaron-marketing:remember`. Old `/seo:*` commands are not runtime aliases — paste into `/aaron-marketing:auto` for recovery routing.
- **Wiki Knowledge Layer (Phase 1 → 3)**: full multi-session memory layer with auto-refreshed index (Phase 1), compiled pages with source SHA-256 hashes and conversational `(a)/(b)/(s)/(i)` contradiction reconciliation (Phase 2), and user-initiated WARM retirement with `originally_at` reverse link for full rollback recovery (Phase 3). New auxiliary files: `memory/wiki/log.md`, `.unresolved.md`, `.drift-log`, `.retire-day-log`. Recovery script `scripts/recover-retired-warm.sh` + Phase 3 rollback validator `scripts/validate-phase3-rollback.sh` (4 fixture variants).
- **Severity-tier routing for auditor outputs (B3)**: `content-quality-auditor` and `domain-authority-auditor` now route findings by severity tier (Critical / High / Medium / Low) instead of flat lists.
- **`/aaron-marketing:remember` slash command**: non-technical-user recovery path with trigger phrases (`recover wiki` / `恢复wiki` / `undo last retire`). memory-management runs recovery scripts on the user's behalf rather than telling them to "Run scripts/recover-retired-warm.sh".
- **Bulk + force retire flows**: `/aaron-marketing:guard --wiki --retire-preview --bulk-confirmed` retires all `safe`-marked candidates in one operation; `force-retire <path>` bypasses C5 (frontmatter-coverage) only. Day-cap (20/UTC-day) still enforced.
- **Multi-project guardrail**: pre-compile prompt when ≥2 distinct project slugs in hot-cache history.
- **PII compile guardrail**: heuristic detection of natural-person entities (title-case names / LinkedIn / `entity_type: person`); surfaces GDPR Art 5(1)(c) data-minimization warning before compile.
- **GDPR purge schema**: honest, minimal template at `cross-cutting/memory-management/references/gdpr-purge-log-template.md` — a human-readable record of erasure requests (date, redacted_label, legal_basis, action, scope, working_tree_only), never raw subject data. Working-tree redaction only; git history is the user's responsibility (no salted fingerprint / reingest tombstone).
- **`/aaron-marketing:series` command**: plan / write / continue / publish-handoff modes for content series workflows.
- **Multi-agent compatibility**: Gemini, Qwen, Amp, Kimi, CodeBuddy manifest support.
- **31 eval cases** under `evals/memory-management/` (was 6 pre-9.5.0) covering retirement, recovery, contradiction reconciliation, GDPR, multi-project, PII, force-retire.

**Fixed (security)**:
- (R1) Symlink-pivot path-injection bypass in `scripts/recover-retired-warm.sh` — `verify_destination_under_memory()` helper uses `pwd -P` resolution + symlink-ancestor walk to stop planted symlinks chasing outside the repo.
- (R2) SessionStart hook prompt-injection — `.unresolved.md` and archive `originally_at:` text now treated as data, sanitized for newlines / control-bytes / backticks before display.
- (Sec #2) Predictable-PID DoS in validator — `/tmp/INJECTION_*_$$` sentinels replaced with `mktemp -d` inside per-test `$TMPDIR`.

**Fixed (code quality)**:
- `set -e` swallowed by `||` chain in `run_fixture` — switched to explicit `if !` chains.
- awk pattern drift between recovery + validator — shared-invariant comment block in both scripts.
- `set -euEo pipefail` + ERR trap with `$LINENO`/`$BASH_COMMAND` for CI debuggability.
- `sed`-based `extract_originally_at()` (was `awk '{print $2}'` — truncated paths with spaces).
- Explicit `mkdir -p` error handling.

**Fixed (CI + UX)**:
- `.github/workflows/validate-skill.yml` sets `actions/checkout@v4 with: fetch-depth: 2`. Without this, `changed_paths_match` in `validate-slimming-guardrails.sh` silently skipped on shallow checkouts.
- `changed_paths_match` emits `info:` stderr line when HEAD~1 is unavailable (skip is now observable).
- Audit-log post-condition mandated for every wiki write — `wiki-runbook §3` log table extended with `restore` + `resolve` operations.

**Changed**:
- Public command API: `/seo:*` → `/aaron-marketing:*` (breaking).
- Skill `version` and `metadata.version` fields unified across all 20 skills.
- Marketplace mirrors (`marketplace.json` ↔ `.claude-plugin/marketplace.json`) kept byte-identical via `.github/scripts/sync-skills.js`.

**Protected**: all 20 skills and 17 commands remain. No skill directories renamed, moved, or deleted. Existing skill GitHub URLs are stable.

- 20 skills (4 research + 4 build + 4 optimize + 4 monitor + 4 cross-cutting).
- CORE-EEAT 80-item content quality framework with three veto items (T04, C01, R10).
- CITE 40-item domain authority framework with three veto items (T03, T05, T09).

### v9.0.0 — Quality pass + multi-agent compatibility (2026-04-17)

Combined quality/compliance hardening, executable playbooks, Gemini/Qwen/Amp/Kimi/CodeBuddy support, `/seo:geo-drift-check`, compact references, handoff coverage, memory scaffolding, and markdown-command maintenance. No breaking changes to skill I/O contracts.

### Earlier releases

Earlier versions are documented in [GitHub Releases](https://github.com/aaron-he-zhu/aaron-marketing-skills/releases).
