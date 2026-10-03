---
title: Create or revise software documentation
cues:
- reader-facing project text, such as documentation or source comments, should be written or changed
goal: The authorized reader-facing project material states the requested software behavior or procedure from established sources of truth, reaches its intended reader, passes evidence sensitive to the reader path, and leaves executable software and operational state unchanged.
knowledge:
- authorized-software-surface
- project-grounding
guides:
- documentation-work
- source-comments
- documentation-evidence
- user-interface-work
- performance-evidence
- security-boundaries
- change-sites
- interface-contracts
- dependency-and-artifact-integrity
- observability-and-diagnostics
- algorithmic-and-numeric-correctness
- commands-and-tooling
- workspace-integrity
- version-control
- work-slicing
handoffs:
- task: implement-change
  applicability:
  - When the documentation cannot be made true without changing executable software, the requester authorized that change, and it is neither made nor pending on this route
---

This task changes documentation only. Its writable surface is the prose, reader-facing text, comments, docstrings, examples, and documentation configuration the request authorizes.

Establish the intended reader, the task or decision the material must support, the current software behavior it describes, and the project location that owns that reader path. Map only the components, boundaries, data or control paths, extension points, operating procedures, and verification mechanisms that the documentation outcome consumes. Do not turn a request about one subsystem into a whole-repository survey. Establish each claim from declarations, configuration, tests, help, history, and implementation paths as it needs.

Decide the reader contract and the evidence that will show the material serves it before drafting. Change only the authorized documentation surface. Verify links, examples, generated results, or other reader-visible behavior with the narrowest evidence sensitive to them, and reconcile every page or navigation edge whose truth changed. A failed check or discovered contradiction reopens the claim, scope, or source decision that produced it rather than authorizing a code change to make the documentation true.

When more than one independently verifiable documentation slice is required, order shared concepts and prerequisites before the pages that depend on them. After the slices pass, follow the combined reader path and inspect the complete documentation diff for unsupported claims, duplication, stale navigation, temporary artifacts, and accidental executable changes.

Report what the intended reader can now do or understand, the documentation surface changed, the decisive validation, and any software or operational mismatch that remains outside this task's write authority.
