---
type: skill
lifecycle: stable
inheritance: master-only
name: coherence-audit
description: Detect coherence violations between Alex_ACT_Edition (brain) and Alex_Skill_Mall (marketplace) — broken references, tag mismatches, deprecated install snippets
tier: standard
applyTo: '"**/Alex_ACT_Edition/.github/**,**/Alex_Skill_Mall/STORES.md,**/Alex_Skill_Mall/CATALOG.md"'
currency: 2026-04-28
lastReviewed: 2026-01-01
---

# Coherence Audit

The brain (Edition) and the Mall must agree. Coherence drift is silent — Edition can recommend a store the Mall has pruned, or the Mall can list a store with a tag the brain contradicts.

## When to Use

- Periodic full audit (recommended monthly, fired by `/audit-coherence`)
- Before any Mall prune that touches a referenced entry
- Before tagging an Edition release (preflight check)
- When a heir reports "the brain told me to use X but the Mall doesn't have it"

## The Three Coherence Checks

| # | Violation | Detection |
|---|---|---|
| 1 | **Broken reference** — Edition cites a store that's no longer in the Mall | Grep `Alex_ACT_Edition/.github/` for store URLs and names; intersect with current `STORES.md` |
| 2 | **Tag mismatch** — Edition tags a store "primary" but Mall doesn't list it as First-Party | Cross-check the brain's "primary" or "recommended" tags against Mall's category headings |
| 3 | **Deprecated snippet** — Mall install snippet uses a command the brain says is deprecated | Cross-grep MCP install snippets in Mall against any `deprecated:` flag in brain instructions |

## Procedure

1. Run `node scripts/coherence-check.cjs` (mechanical sweep — covers Check 1, partial Check 2)
2. For each finding, classify:
   - **Hard violation** — broken reference, must fix before any release
   - **Soft violation** — tag drift, fix in next routine sweep
   - **False positive** — string match without semantic meaning (e.g., a URL in a code example)
3. Run an ACT pass on the verdict — coherence fixes touch both repos
4. For each hard violation, decide which side fixes:
   - Edition references a pruned store → fix Edition (remove or replace reference)
   - Mall pruned a store Edition still legitimately needs → re-add to Mall (run [store-evaluation](../store-evaluation/SKILL.md))
   - Tag mismatch → align the side that's wrong (usually Edition, since Mall is the catalog of record)
5. Open coordinated PRs (Edition + Mall) when both sides need changes
6. Record in `decisions/curation-log.md`

## Hard Rules

1. **Mall is the catalog of record** — when names or URLs disagree, the Mall wins (it's the marketplace; Edition consumes it).
2. **Edition is the doctrine of record** — when capability claims disagree (deprecated, primary, recommended), the Edition's brain wins.
3. **Coherence-check is a release gate** — Edition releases must pass coherence-check; if a violation exists, either fix it or document the exception in the release notes.
4. **No silent suppressions** — every "false positive" finding gets a one-line note in the audit report explaining why.

## Decision Matrix

| Edition says | Mall says | Verdict |
|---|---|---|
| Cites store X | Has X in catalog | OK |
| Cites store X | No X | Hard violation — fix Edition or re-add to Mall |
| Tags X "primary" | Lists X in First-Party | OK |
| Tags X "primary" | Lists X in Community | Soft violation — align tags |
| Says command Y deprecated | Mall snippet uses Y | Soft violation — refresh Mall snippet |
| Recommends X for use case Z | No X | Hard violation |

## Output Template

```markdown
# Coherence Audit — YYYY-MM-DD

## Scope

- Edition: <commit SHA>
- Mall: <commit SHA>

## Mechanical Findings

| Finding | Type | Side to fix | Severity |
|---|---|---|---|

## Semantic Findings

| Finding | Type | Side to fix | Severity |
|---|---|---|---|

## Coordinated PRs

- Edition: <PR link or "none">
- Mall: <PR link or "none">

## False Positives

| Finding | Why it's not a violation |
|---|---|

## ACT Pass Trail

<markers>
```

## Anti-Patterns

| Anti-pattern | Correction |
|---|---|
| Fixing Edition only when Mall is the catalog of record | Catalog-of-record rule decides which side moves |
| Suppressing findings without rationale | Every dismissed finding gets a one-line note |
| Running coherence-check on stale Mall data | Always run after a Mall pull, not before |
| Treating string-match as definitive | Some matches are illustrative URLs in examples; classify as false positive |

## Related

- [mall-curation](../mall-curation/SKILL.md), [staleness-discipline](../staleness-discipline/SKILL.md)
- [skill-review](../skill-review/SKILL.md) — Edition-side gate that prevents new violations at PR time
- `/audit-coherence` prompt
- `scripts/coherence-check.cjs` mechanical sweep
