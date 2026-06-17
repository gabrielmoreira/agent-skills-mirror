# Plan Audit Checklist

Review these areas before approving a plan:

1. Are the referenced files and paths real?
2. Do phases have clear objectives and non-overlapping responsibilities?
3. Are same-wave phases writing to the same files or contracts?
4. Are acceptance criteria objectively testable?
5. Are validation commands or verification mechanisms concrete enough?
6. Does any destructive or migration-heavy phase have rollback or recovery guidance?
7. Are there missing dependency assumptions, version assumptions, or unpinned external contracts?
8. Did the plan apply the Minimum Viable Change Ladder before proposing a new abstraction, new dependency, or new generated surface?
9. Would a fresh executor be blocked by ambiguity in the first 1-3 phases?
10. Does the plan promise scope that the listed phases never actually implement?
11. Do security, access control, or operability concerns deserve stronger gates than the plan currently shows?
