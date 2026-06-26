# Review Checklist

Review in this order:

1. Does the change violate the intended behavior or user request?
2. Could it corrupt data, skip validation, leak access, or break authorization?
3. Could it introduce race conditions, ordering bugs, or state divergence?
4. Does it create performance or scale regressions on likely hot paths?
5. Did it drift from the plan, contract, schema, or accepted scope?
6. Are tests missing for the riskiest behavior?
7. Are docs, migration notes, or operational steps missing where required?

## Change Size and Signal

- Treat reviews much larger than roughly 100 changed lines as lower-signal unless the diff is mechanical or tightly scoped.
- Ask for a split when a diff mixes unrelated behaviors, generated output, policy changes, and implementation edits.
- If a large review cannot be split, review by file area and risk axis and state confidence limits.

## Over-Engineering Pass

- After correctness, security, data integrity, and scope checks, ask what can delete, inline, or replace with a standard library or native platform feature.
- Flag one-use abstractions, speculative configuration, wrappers with no policy value, and new dependencies that an already-installed dependency or platform primitive covers.
- Treat over-engineering as a maintainability signal. Block only when it creates real review, behavior, test, dependency, or operability risk; otherwise report it as a non-blocking simplification opportunity.

## Stop-the-Line Decision Points

Halt for security, authorization, secret-handling, destructive-action, or data-integrity defects; failed core behavior or acceptance criteria; migration/schema/contract changes without rollback or compatibility evidence; or scope drift that prevents comparison to the approved plan.

## Five-Axis Prompts

- Correctness & Functionality: requested behavior, edge cases, and regressions.
- Security: authorization, secrets, inputs, data boundaries, and destructive operations.
- Architecture & Design: ownership, dependencies, schemas, lifecycle boundaries, and rollback expectations.
- Maintainability & Style: simple, localized, idiomatic, and free of unrelated cleanup.
- Test Quality & Coverage: observable behavior, correct boundary, and evidence matching the completion claim.
