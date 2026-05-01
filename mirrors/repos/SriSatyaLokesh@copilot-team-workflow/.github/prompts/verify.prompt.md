---
description: 'Verify a Issue is complete, tested, and documented — final check before PR'
agent: 'Verify'
---
Verify this Issue is complete and ready to merge.

Check:
1. All Phase 1 requirements are implemented
2. All Phase 3 plan tasks are complete
3. Tests pass (run npm test)
4. API docs are updated
5. Code quality: no TS errors, no lint errors

Issue doc: ${input:ISSUE-doc:Path to Issue doc (e.g., docs/Issues/ISSUE-042-name.md)}

Generate a verification report and update Phase 5 in the Issue doc.
