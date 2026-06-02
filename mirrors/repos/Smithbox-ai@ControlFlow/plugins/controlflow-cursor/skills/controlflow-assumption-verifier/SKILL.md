---
name: controlflow-assumption-verifier
description: "Use when a saved plan may contain hidden assumptions disguised as facts, especially for medium or large tasks, unresolved high-risk plans, or plans that mention files, APIs, versions, integrations, tests, or concurrency patterns that should be verified against the repository before execution."
---

# ControlFlow Assumption Verifier

## Overview

Hunt mirages in a saved plan. This skill adapts ControlFlow's AssumptionVerifier to Codex by checking whether the plan invents files, APIs, dependencies, conventions, or execution assumptions that the repository does not support.

## Workflow

1. Read the saved plan artifact first.
2. For each important claim in the plan:
   - identify the claim
   - decide whether it is repository-verifiable
   - verify it against files, paths, symbols, configs, or tests
   - classify it as `VERIFIED`, `UNVERIFIED`, or `MIRAGE`
3. Use [references/mirage-patterns.md](references/mirage-patterns.md) as the review grid.
4. Focus especially on:
   - phantom paths
   - phantom APIs
   - missing dependencies
   - pattern mismatches
   - missing error paths
   - missing migrations
   - missing security boundaries
5. Save the verdict to `plans/artifacts/<task-slug>/assumption-verifier.md` using `../../templates/assumption-verifier-report-template.md`.
6. Return a structured text report with:
   - `COMPLETE` or `ABSTAIN`
   - blocking and minor mirages
   - a dimensional scorecard
   - a recommendation
7. If the plan requires meaningful redesign, classify it as:
   - `fixable`
   - `needs_replan`
   - `escalate`

## Output Shape

- **Status**
- **Mirages Found**
- **Dimensional Scores**
- **Summary**
- **Failure Classification** when blocking issues exist

## Common Mistakes

- Treating every unknown as a mirage instead of separating `UNVERIFIED` from `MIRAGE`.
- Checking only presence claims and skipping missing requirements or edge cases.
- Reviewing the plan abstractly without actually opening the referenced files or paths.

## References

- `references/mirage-patterns.md`
- `../../templates/assumption-verifier-report-template.md`
