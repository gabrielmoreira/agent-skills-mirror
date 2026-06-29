# Contributing

Thanks for your interest in contributing! This guide covers adding skills, improving existing ones, and submitting changes.

## Requesting a Skill

[Open a Skill Request issue](https://github.com/aaron-he-zhu/aaron-marketing-skills/issues/new?template=skill-request.yml) if you have an idea but don't want to build it yourself.

## Adding a New Skill

### 1. Choose the correct category

| Category | Directory | Use when the skill... |
|----------|-----------|----------------------|
| Research | `research/` | Gathers market data before content creation (SEO/GEO) |
| Build | `build/` | Creates new content or markup (SEO/GEO) |
| Optimize | `optimize/` | Improves existing content or site health (SEO/GEO) |
| Monitor | `monitor/` | Tracks performance over time (SEO/GEO) |
| Cross-cutting | `cross-cutting/` | Spans multiple phases (quality frameworks, entity, memory) |
| Insight | `insight/` | Understands audience, niche, trends (influencer/IMPACT) |
| Map | `map/` | Discovers and scores influencers (influencer/IMPACT) |
| Plan | `plan/` | Designs campaigns, briefs, budgets (influencer/IMPACT) |
| Activate | `activate/` | Runs outreach, content review, contracts (influencer/IMPACT) |
| Convert | `convert/` | Amplifies and repurposes content (influencer/IMPACT) |
| Track | `track/` | Measures performance and ROI (influencer/IMPACT) |

### 2. Create the skill directory

```bash
mkdir -p <category>/<skill-name>
```

Directory name: 1-64 chars, lowercase `a-z`, numbers, hyphens only. No leading/trailing/consecutive hyphens.

### 3. Create `SKILL.md` with required frontmatter

```yaml
---
name: your-skill-name
version: "1.0.0"
description: 'Use when the user asks to "[trigger]". [What it does]. For [related task], see [other-skill].'
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
metadata:
  author: your-github-username
  version: "1.0.0"
  geo-relevance: "high|medium|low"
  tags: [seo, your-tags]
  triggers: ["trigger phrase 1", "trigger phrase 2"]
---
```

The `name` field must match the directory name exactly.

### 4. Write effective instructions

Use the compact shared skeleton from `references/skill-contract.md`: `Quick Start`, `Skill Contract`, `Handoff Summary`, `Data Sources`, `Instructions`, `Reference Materials`, and `Next Best Skill`. Optional sections such as `What This Skill Does`, `Example`, `Tips for Success`, `Save Results`, and `Validation Checkpoints` are welcome when they improve execution quality. Put detailed references in the skill's `references/` subdirectory.

Auditor-class skills are the exception: they inline the authoritative auditor runbook directly in their `SKILL.md` body.

### 5. Validate

```bash
./scripts/validate-skill.sh <category>/<skill-name>
```

### 6. Update tracking files

After adding or updating a skill, keep these **8 tracking files** in sync. **This list is authoritative** — `CLAUDE.md` and `AGENTS.md` point here instead of restating it, so update this list if the set changes.
- `VERSIONS.md` — version and date
- `.claude-plugin/plugin.json` — skills array + version
- `marketplace.json` (repo root) — must match plugin.json
- `.claude-plugin/marketplace.json` — **byte-identical mirror** of the root `marketplace.json` (copy it after editing the root)
- `README.md` — skills table + version badge
- `CLAUDE.md` — category table + version
- `AGENTS.md` — name/count line + framework item/dimension counts
- `docs/README.zh.md` — Chinese README: the 38 / 20 / 18 / 5 counts + version badge

For release bumps, also sync README badges and localized README badges.

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
