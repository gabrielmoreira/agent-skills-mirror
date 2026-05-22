---
type: instruction
lifecycle: stable
inheritance: inheritable
description: Brain audit routing -- run local deterministic QA, validate findings in files, and prioritize fixes by severity.
application: When the user asks for a brain audit, quality audit, or consistency review of Edition artifacts.
applyTo: '**/*audit*brain*,**/*brain*qa*,**/*epistemic*qa*,**/*quality*review*'
currency: 2026-05-13
lastReviewed: 2026-05-13
---

# Brain Audit Routing

For any brain-audit request:

1. Route through `/audit-brain` and run the `brain-auditor` worker first.
2. Use local deterministic evidence (frontmatter/schema consistency, manifest consistency, cross-reference integrity).
3. Validate each finding in the target file before proposing changes.
4. Apply minimal fixes to high-severity findings first, then medium, then low.
5. Rerun the same local evidence checks after edits.

The audit is complete only after findings are either fixed or explicitly documented as deferred with rationale.

## Would Revise If

Revise if the brain-auditor worker misses defect classes that manual review catches on the same audit pass, if local deterministic checks repeatedly disagree with file-validated findings (the muscle is unreliable), or if severity prioritization causes critical defects to ship while medium ones get fixed first.
