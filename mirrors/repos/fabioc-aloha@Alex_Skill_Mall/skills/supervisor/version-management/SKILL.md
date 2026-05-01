---
type: skill
lifecycle: stable
name: "version-management"
inheritance: master-only
description: "Semver discipline for Alex_ACT_Edition — bump rules, breaking-change classification, fleet rollout sequencing"
tier: standard
applyTo: '**/*version*,**/CHANGELOG*,**/package.json,**/*.bicep'
currency: 2026-04-28
lastReviewed: 2026-01-01
---

# Version Management

> The Edition has a version. Heirs depend on it. Bumping it wrong breaks the fleet.

## When to Use

- Cutting a new release of `Alex_ACT_Edition` (template repo)
- Classifying an incoming PR as patch / minor / major
- Reviewing whether an Edition change is breaking for deployed heirs
- Coordinating a phased rollout when a major version ships

## Semver Rules for the ACT-Edition

The Edition is a **template** that heirs copy. The contract is therefore:

| Bump | What it means | Examples |
| --- | --- | --- |
| **Patch** (`x.y.Z`) | Internal-only fixes; no heir-visible behavior change | typo in a SKILL.md, internal script refactor that produces identical output |
| **Minor** (`x.Y.0`) | Additive changes; heirs that ignore the new artifact still work | new skill, new instruction, new prompt, new optional config field |
| **Major** (`X.0.0`) | Breaking changes; heirs must update or stay pinned | renaming a skill, deleting a skill heirs reference, frontmatter schema change, mandatory new config field, behavior change of an existing skill |

### The "would a heir notice?" test

For every PR you're reviewing for release, ask: *if a heir is on the previous version and never updates, does this change break them?*

- **No, completely invisible** → patch
- **No, they just don't get the new thing** → minor
- **Yes, something they depend on is gone or changed** → major

## Breaking-Change Classification

Five categories of breaking change. All require a **major** bump:

| Category | Example | Required action |
| --- | --- | --- |
| Removal | Deleting a skill | Add to deprecation log, ship in N-1 with deprecation notice first |
| Rename | `feedback-triage` → `submission-triage` | Provide alias in N-1, remove alias in N+1 |
| Frontmatter schema | New required field on all SKILL.md | Migration script in release notes |
| Behavior change | Same skill name now does X instead of Y | Major bump only — do not silently change |
| Required config | New mandatory key in `.github/config/*.json` | Migration script + clear error if absent |

## Deprecation Protocol

Never delete in one release. Always two-step:

1. **Deprecate (minor bump)** — add `lifecycle: deprecated` to the artifact's frontmatter, add a `## Deprecated` section explaining the replacement, keep it functional. Add to `decisions/deprecations.md`.
2. **Remove (major bump)** — at least one full release later, delete the artifact. The major version signals heirs to update.

A heir running N-1 should always have a working brain. The only path to "this no longer works" is a deliberate major upgrade.

## Release Sequencing

For a major release with breaking changes:

1. Run `release-preflight` skill for mechanical gates
2. Run `coherence-audit` to verify Edition ↔ Mall consistency
3. Cut the release on Edition repo (tag, CHANGELOG, GitHub release)
4. Post fleet announcement (when fleet announcement infra exists)
5. Wait observation window (2 weeks for major, 1 week for minor)
6. Triage feedback that arrives in `feedback/inbox/`

For patch and minor: steps 1–3 only, no announcement, no observation window.

## Visible Markers

Every release decision records these in `decisions/curation-log.md`:

| Marker | When |
| --- | --- |
| `Bump: patch\|minor\|major` | Every release |
| `Breaks: <list of categories>` | Every major bump |
| `Deprecated: <list>` | Every minor that introduces deprecations |
| `Removed: <list>` | Every major that completes a deprecation |

## Anti-Patterns

| Anti-pattern | Correction |
| --- | --- |
| Silent rename to "improve discoverability" | Major bump with alias path |
| Patch bump that ships a new skill | Minor bump — additive but not invisible |
| Major bump for typo fix | Patch bump — heirs don't notice |
| One-shot deletion without deprecation step | Two-step: deprecate in N, remove in N+1 |
| Calling a behavior change "a fix" | Behavior changes are always major, regardless of intent |

## Falsifiability

This skill has failed if any of these occur within 90 days of any Edition release:

- A heir reports breakage from an N-1 → N upgrade we classified as patch or minor
- A removal lands without a deprecation notice in the prior release
- The curation-log lacks the required `Bump:` marker for any release

Track in `decisions/curation-log.md`. If two failures occur in 90 days, retire this skill and re-author from observed evidence.
