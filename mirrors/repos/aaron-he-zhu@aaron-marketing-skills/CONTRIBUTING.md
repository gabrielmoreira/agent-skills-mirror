# Contributing

Thanks for your interest in contributing! This guide covers adding skills, improving existing ones, and submitting changes.

## Requesting a Skill

[Open a Skill Request issue](https://github.com/aaron-he-zhu/aaron-marketing-skills/issues/new?template=skill-request.yml) if you have an idea but don't want to build it yourself.

## Adding a New Skill

### 1. Choose the correct category

| Category | Directory | Use when the skill... |
|----------|-----------|----------------------|
| Research | `seo-geo/research/` | Gathers market data before content creation (SEO/GEO) |
| Build | `seo-geo/build/` | Creates new content or markup (SEO/GEO) |
| Optimize | `seo-geo/optimize/` | Improves existing content or site health (SEO/GEO) |
| Monitor | `seo-geo/monitor/` | Tracks performance over time (SEO/GEO) |
| Protocol | `protocol/` | Cross-cutting layer (truth registries: entity/creator/claims/consent/launch + memory) — shared across disciplines |
| Discover | `influencer/discover/` | Audience/niche mapping + influencer discovery & fit (influencer) |
| Plan | `influencer/plan/` | Competitor tracking, campaigns, briefs, budgets (influencer) |
| Activate | `influencer/activate/` | Outreach, content review (C³ ART gate), contracts, amplification (influencer) |
| Measure | `influencer/measure/` | Post-click, performance, ROI, reports (influencer) |
| Paid Ads | `ad/<phase>/` | Builds, audits, and scales paid-ad campaigns (ROAS loop: research/orchestrate/activate/scale) |
| Email | `email/<phase>/` | Grows, sends, and audits email programs (SEND loop: setup/engage/nurture/deliver) |
| Launch | `launch/<phase>/` | Plans, gates, executes, and proves product launches (RAMP loop: research/assemble/mobilize/prove) |
| Social | `social/<phase>/` | Plans, crafts, hosts, and measures organic social (ECHO loop: explore/craft/host/observe) |
| Narrative | `narrative/<phase>/` | Traces, architects, lands, and proves brand narrative & messaging (TALE loop: trace/architect/land/evaluate) |

### 2. Create the skill directory

```bash
mkdir -p <category>/<skill-name>
```

Directory name: 1-64 chars, lowercase `a-z`, numbers, hyphens only. No leading/trailing/consecutive hyphens.

### 3. Create `SKILL.md` with required frontmatter

```yaml
---
name: your-skill-name
slug: aaron-your-skill-name
displayName: "Your Skill Name · 中文名"
summary: "一句话中文简介(SkillHub.cn 列表卡片)"
version: "1.0.0"
description: 'Use when the user asks to "[trigger]". [What it does]. For [related task], see [other-skill].'
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
metadata: {"author": "your-github-username", "version": "1.0.0", "discipline": "seo-geo", "phase": "research", "geo-relevance": "high|medium|low", "hermes": {"tags": ["marketing", "seo-geo", "research"], "category": "seo-geo"}, "openclaw": {"emoji": "🔍", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---
```

The `name` field must match the directory name exactly. `metadata` must be a **single-line strict-JSON object** (valid YAML flow mapping) — OpenClaw's frontmatter parser reads single-line keys only, and the validator fails a YAML block map. In single-quoted scalars, double any literal apostrophe (`designer''s`). Keep the `hermes` (tags/category) and `openclaw` (emoji/homepage) host extensions in step with the skill's discipline. The `slug`/`displayName`/`summary` trio is the [SkillHub.cn](https://skillhub.cn) publishing contract — `slug` must be the platform-owned frontmatter slug (`<skill-name>` when available, otherwise `aaron-<skill-name>` as the conflict fallback; validator-enforced), `displayName` bilingual, `summary` a Chinese one-liner.

### 4. Write effective instructions

Use the compact shared skeleton from `references/skill-contract.md`: `Quick Start`, `Skill Contract`, `Handoff Summary`, `Data Sources`, `Instructions`, `Reference Materials`, and `Next Best Skill`. Optional sections such as `What This Skill Does`, `Example`, `Tips for Success`, `Save Results`, and `Validation Checkpoints` are welcome when they improve execution quality. Put detailed references in the skill's `references/` subdirectory.

Auditor-class skills are the exception: they `Read references/auditor-runbook.md` at activation (the framework-agnostic SSOT: handoff schema, cap method, Artifact Gate, translation format) via a plugin-relative path, and keep only their framework-specific §2 worked examples, §3 guardrails, and §5 veto-ID rows inline in the `SKILL.md` body. Eight skills are auditor-class gate consumers, each scored against one framework and writing to its own audit sink:

| Auditor-class skill | Framework | Audit sink |
|---------------------|-----------|------------|
| `content-quality-auditor` | CORE-EEAT (publish readiness) | `memory/audits/content/` |
| `domain-authority-auditor` | CITE (citation trust) | `memory/audits/domain/` |
| `content-reviewer` | C³ ART (influencer content gate) | `memory/audits/influencer/` |
| `ad-account-auditor` | ROAS RQS (paid-ads gate) | `memory/audits/ad/` |
| `email-quality-auditor` | SEND EQS (email SEND gate) | `memory/audits/email/` |
| `launch-readiness-auditor` | RAMP LQS (launch readiness gate) | `memory/audits/launch/` |
| `social-quality-auditor` | ECHO SQS (organic-social gate) | `memory/audits/social/` |
| `narrative-quality-auditor` | TALE NQS (brand-narrative gate) | `memory/audits/narrative/` |

Cross-cutting reference protocols apply across disciplines: the humanizer-slop protocol, the measurement-protocol decision protocol, and the per-channel `platforms/` reference packs. These stay references (not skills) by design — each is consumed as a pre-handoff sub-step inside discipline skills, so promoting one to a standalone skill would duplicate that step.

### 5. Validate

```bash
./scripts/validate-skill.sh <category>/<skill-name>
```

CI runs additional guards beyond the per-skill validator:
- **golden-math** — validates the rollup math for all **eight** quality frameworks: CORE-EEAT (80-item content quality, SEO/GEO), CITE (40-item domain authority, SEO/GEO), C³ (influencer — ACE/ART/ROI with CVI geometric-mean rollup, veto ACE A2/C1/E2 + ART T1/T2), ROAS (paid ads — R Return / O Offer / A Audience / S Spend-efficiency, RQS arithmetic weighted-mean rollup like CITE, veto R1/R2/O1/O2/A1; see [references/roas-benchmark.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/roas-benchmark.md)), SEND (email — S Sender-integrity/deliverability / E Engagement / N Nurture-lifecycle / D Direct-response, EQS arithmetic goal-weighted-mean rollup like ROAS, veto S1/S2/N1/D1; see [references/send-benchmark.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/send-benchmark.md)), RAMP (launch — R Readiness / A Assets / M Momentum / P Proof, LQS arithmetic goal-weighted-mean rollup like SEND, veto RAMP R1/A1/M1/P1 with framework-name qualification against the ROAS ID collision; see [references/ramp-benchmark.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/ramp-benchmark.md)), ECHO (organic social — E Embeddedness / C Craft / H Hosting / O Observability, SQS arithmetic goal-weighted-mean rollup like RAMP, veto ECHO E1/C1/C2/H1/H2/O1 with framework-name qualification against the ROAS O1 ID collision; see [references/echo-benchmark.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/echo-benchmark.md)), and TALE (brand narrative — T Truth / A Architecture / L Landing / E Evidence, NQS arithmetic goal-weighted-mean rollup like ECHO, veto TALE T1/A1/L1/E1 with framework-name qualification against the ECHO-E1 and ROAS/RAMP-A1 ID collisions; see [references/tale-benchmark.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/tale-benchmark.md)).
- **check-evals** — structural lint over the eval fixtures.
- **check-pii** — scans for committed PII.
- **check-stdlib-only** — enforces the zero-dependency Python-stdlib rule for connector helpers, including the Paid-Ads keyed-API red line (no keyed paid-ad API calls baked into skills).

### 6. Update tracking files

After adding or updating a skill, keep these **9 tracking surfaces** in sync. **This list is authoritative** — `CLAUDE.md` and `AGENTS.md` point here instead of restating it, so update this list if the set changes.
- `VERSIONS.md` — version and date
- `.claude-plugin/plugin.json` — skills array + version
- `marketplace.json` (repo root) — must match plugin.json
- `.claude-plugin/marketplace.json` — **byte-identical mirror** of the root `marketplace.json` (copy it after editing the root)
- `README.md` — skills table + version badge
- `CLAUDE.md` — category table + version
- `AGENTS.md` — name/count line + framework item/dimension counts (CORE-EEAT / CITE / C³ / ROAS / SEND / RAMP / ECHO / TALE)
- `docs/README.zh.md` — Chinese README: the 120 · 16 / 16 / 16 / 16 / 16 / 16 / 16 / 8 counts (skills / SEO-GEO / influencer / paid ads / email / launch / social / narrative / protocol) + 8 commands + version badge. The 8 additional localized READMEs (`docs/README.{de,es,fr,it,ja,ko,pt,zh-Hant}.md`) are now version-locked too — `check-versions.sh` asserts each carries the current `version-<bundle>-orange` badge (the bundle value is read from `plugin.json`, so this never goes stale on a bump).
- `.github/repo-about.json` — the GitHub repo **About** SSOT (sidebar description + topics). The About is *not* read by GitHub directly and *not* editable by the CI token, so it silently drifted on the v13/v14 discipline bumps. Edit the count/disciplines/gates here, then project it onto GitHub with `bash scripts/sync-about.sh --live` (owner-run, needs admin auth). `check-versions.sh` asserts its skill count matches the tree; the weekly `about-drift.yml` sentinel fails red if GitHub drifts from it.

For release bumps, also sync README badges and localized README badges.

**Adding or renaming a skill?** Also add its slug to a grouping in the repo-root `skills.sh.json` — the [skills.sh registry page](https://skills.sh/aaron-he-zhu/aaron-marketing-skills) renders those sections, and CI fails when the groupings don't cover exactly the plugin.json skill set (an ungrouped skill would render below the legacy names at the bottom of the page).

**Cutting a release?** Also (a) sync the downstream repo family: `bash scripts/sync-family.sh` (dry-run drift report), then `bash scripts/sync-family.sh --live` to push the live mirrors — registry, tiers, and banner templates in [docs/repo-family.md](docs/repo-family.md); (b) project the GitHub About: `bash scripts/sync-about.sh` (dry-run), then `bash scripts/sync-about.sh --live`; and (c) distribute to the registries — `bash scripts/registry-status.sh` to see per-skill drift across ClawHub + SkillHub, then `bash scripts/publish-registries.sh --live` (publishes only the behind-set) and `bash scripts/publish-package.sh --live` (the OpenClaw bundle-plugin). Full runbook: [docs/distribution.md](docs/distribution.md). All owner-run (editing external/GitHub/registry state needs auth the CI token lacks). Between releases, the weekly `family-drift.yml` and `about-drift.yml` sentinels fail red if either surface drifts.

**CI enforces this list**: `scripts/check-versions.sh` fails the build when the bundle version drifts across plugin.json / the marketplace mirrors / the README badges / CLAUDE.md / VERSIONS.md, when any SKILL.md version disagrees with its VERSIONS.md row, or when `.github/repo-about.json`'s skill count disagrees with the tree — so a missed file surfaces in the PR, not in a user's session. Run it locally before pushing: `bash scripts/check-versions.sh`.

**Adding a connector?** Follow [docs/connector-playbook.md](docs/connector-playbook.md) — the end-to-end pipeline (qualify → verify → implement → test → wire → document → track → regress → record) with the safety-class gate table and the connector-vs-recipe decision rule.

## Improving Existing Skills

Keep changes focused. Bump both top-level `version` and `metadata.version` together. Update `VERSIONS.md`. Put new reference docs in the skill's `references/` subdirectory.

## Craft Checklist

Beyond the mechanical checks, every skill should pass the senior self-test from [skill-contract.md §Skill Authoring Discipline](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/skill-contract.md):

- [ ] **Simplicity** — would a senior engineer call this skill overcomplicated? Every section traces to the user's task.
- [ ] **Boundary** — the `description` ends with a `Not for X — use Y` clause so it doesn't compete with a sibling skill.
- [ ] **Verifiable** — the Skill Contract states a `Done when:` with checkable conditions.
- [ ] **Honest data** — Instructions tell the model to label Measured / User-provided / Estimated and never invent numbers.
- [ ] **Surgical handoff** — Next Best Skill points to exactly one primary move.

## Quality Checklist (mechanical)

Before submitting a PR:

- [ ] `name` matches directory name (lowercase slug `^[a-z0-9][a-z0-9-]*$`)
- [ ] Top-level `version` is present and matches `metadata.version` plus `VERSIONS.md`
- [ ] `description` includes trigger phrases AND scope boundaries (≤1024 chars)
- [ ] Shared compact section contract present (`validate-skill.sh` checks this)
- [ ] Validator passes: `./scripts/validate-skill.sh <category>/<skill-name>`
- [ ] Uses `~~placeholder` pattern for tool references
- [ ] `allowed-tools: WebFetch` added if skill fetches live URLs
- [ ] Includes validation checkpoints and at least one example
- [ ] All tracking and release files updated; plugin.json and marketplace.json arrays identical
- [ ] `.claude-plugin/marketplace.json` byte-identical to repo-root copy

## Submitting

- Fork, create a `feature/your-skill-name` branch, and submit a PR.

## Code of Conduct

Be respectful, constructive, and focused on making the library better for everyone.
