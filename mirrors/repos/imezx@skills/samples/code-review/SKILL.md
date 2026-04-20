# code-review

Use this skill when asked to review, audit, critique, or improve any piece of code.

---

## Review Order

Always work through these layers in order. Never skip a layer even if earlier ones look fine.

1. **Correctness** - Does it do what it claims? Are edge cases handled?
2. **Security** - Injection, unvalidated input, exposed secrets, unsafe deserialization.
3. **Reliability** - Error handling, null safety, resource cleanup, race conditions.
4. **Performance** - Unnecessary loops, missing indexes, N+1 queries, unbounded memory.
5. **Readability** - Naming, function length, cyclomatic complexity, dead code.
6. **Style** - Conventions consistent with the surrounding codebase.

---

## Output Format

Structure your review as follows:

```
## Summary
One paragraph: overall quality signal and the single most important finding.

## Critical (must fix)
Issues that will cause bugs, data loss, or security vulnerabilities.
For each: problem -> why it matters -> specific fix with corrected code snippet.

## Warnings (should fix)
Issues that degrade reliability or maintainability.
Same format: problem -> why -> fix.

## Suggestions (nice to have)
Style, readability, or minor performance improvements.
Brief - one sentence per item is enough.

## Positive notes (optional)
What is done well. Skip if nothing stands out.
```

---

## Rules

- Never rewrite the entire file unprompted. Fix what was asked about.
- Every Critical and Warning item must include a concrete corrected snippet - not just a description.
- If you are uncertain whether something is a bug or intentional design, say so explicitly.
- Do not flag style issues as Critical. Severity must be accurate.
- If the code is in a specific language, apply language-idiomatic standards (e.g. `Result` types in Rust, `Option` chaining in Swift, `context.Context` propagation in Go).

---

## Language-Specific Gotchas

See `language-notes.md` for common pitfalls per language to check during review.

---

## Severity Definitions

| Level | Meaning |
|---|---|
| Critical | Will cause a bug, crash, or security issue in production |
| Warning | Degrades quality, reliability, or maintainability |
| Suggestion | Improvement only - no functional impact |
