---
type: skill
lifecycle: stable
inheritance: master-only
name: skill-review
description: Review submissions to Alex_ACT_Edition for ACT spec compliance, content quality, and scope fit
tier: standard
applyTo: '"**/*.skill.review.md,**/Alex_ACT_Edition/**"'
currency: 2026-04-28
lastReviewed: 2026-01-01
---

# Skill Review

Evaluate a candidate skill, instruction, or prompt for inclusion in `Alex_ACT_Edition` (the heir template). The Supervisor accepts only what passes all four gates below.

## When to Use

- A PR opens against `Alex_ACT_Edition` proposing a new skill/instruction/prompt
- A `.skill.review.md` file lands in `Alex_ACT_Supervisor/feedback/inbox/`
- A heir's curation log proposes promoting a custom skill to the Edition template
- Triage routes a feedback item to "Edition fix"

## The Four Gates

A submission must pass **all four** to be merged. Failure on any gate = rejection or revision.

### Gate 1 — Spec Compliance

| Check | Pass criterion |
|---|---|
| Frontmatter present | YAML block with `type`, `lifecycle`, `inheritance`, `description`, `application`, `applyTo`, `currency` |
| `applyTo` glob is non-empty | At least one path pattern, no `**/*` unless explicitly justified |
| `inheritance` set correctly | `inheritable` for fleet-wide; `custom` for heir-only; `master-only` reserved for Supervisor/AlexMaster |
| File location matches type | `*.instructions.md` in `instructions/`, `SKILL.md` in `skills/<name>/`, `*.prompt.md` in `prompts/` |
| Markdown lints clean | No broken links, no missing code-fence languages |

### Gate 2 — Content Quality

| Check | Pass criterion |
|---|---|
| Single responsibility | The artifact does one thing; if title contains "and" or "+", split it |
| Behavioral, not encyclopedic | Tells the agent what to *do*, not what a topic *is* |
| Has falsifiability or visible markers | The reader can tell whether the artifact fired correctly |
| ≤ 300 lines (skills) / ≤ 200 lines (instructions) | Longer = signal of overload; split or trim |
| No duplicated content from existing artifacts | Grep for overlapping descriptions across `.github/instructions/` |

### Gate 3 — Scope Fit

| Check | Pass criterion |
|---|---|
| ACT-Edition target | Belongs in the heir template, not in AlexMaster or a different edition |
| Not framework-level | Does not modify ACT manifesto, tenets, or claims registry — that's AlexMaster's territory |
| Not a one-off project script | A skill must generalize to ≥2 projects; if only one heir would ever use it, it's `custom`, not `inheritable` |
| Doesn't duplicate Skill Mall content | If the value is a marketplace listing, it goes in `Alex_Skill_Mall`, not the Edition |

### Gate 4 — Safety

| Check | Pass criterion |
|---|---|
| No destructive defaults | Anything that deletes, force-pushes, or overwrites must require explicit user approval |
| No hardcoded credentials or PII | Run `pii-memory-filter` mentally over the diff |
| No prompt-injection vectors | If the artifact reads external content (URLs, files), it sanitizes or quotes it |
| Reversible | A user can disable or remove the artifact without breaking the Edition |

## Decision Matrix

| Gates passed | Action |
|---|---|
| All 4 | **Accept** — merge and add to next Edition release |
| 3 of 4 | **Request revision** — leave a review comment naming the failed gate |
| 2 of 4 or fewer | **Reject** — close the PR with a written rationale; add to `decisions/` if the rejection sets precedent |

## Output Template

When the review completes, write a verdict to `feedback/inbox/<submission-id>.review.md`:

```markdown
# Review: <submission title>

**Submission**: <path or PR#>
**Reviewer**: Supervisor
**Date**: <ISO date>
**Verdict**: Accept | Request revision | Reject

## Gate Results

- Gate 1 (Spec): Pass / Fail — <details>
- Gate 2 (Quality): Pass / Fail — <details>
- Gate 3 (Scope): Pass / Fail — <details>
- Gate 4 (Safety): Pass / Fail — <details>

## Rationale

<2-3 sentence summary of the verdict>

## Required Changes (if revision)

- <bullet list of concrete asks>

## ACT Pass Trail

<paste the trimmed act-pass markers from the review>
```

## Anti-Patterns

| Anti-pattern | Correction |
|---|---|
| Approving because the submitter is confident | Confidence ≠ quality. Run all four gates regardless of submitter |
| Rejecting without naming the gate | Always cite the specific gate; vague rejections waste cycles |
| Accepting "trivial" submissions without review | Trivial-looking submissions are where regressions hide |
| Reviewing without an `act-pass` trail | This is medium-stakes work — the trimmed pass is mandatory |

## Related

- [brain-curation-rules](../../instructions/brain-curation-rules.instructions.md) — when this skill fires
- [act-pass](../../instructions/act-pass.instructions.md) — required for every review
- `/review-skill` prompt — slash-command entry point
