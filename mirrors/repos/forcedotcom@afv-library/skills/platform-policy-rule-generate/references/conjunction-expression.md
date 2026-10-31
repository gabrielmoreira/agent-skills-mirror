# Conjunction Expressions

Conditions are numbered in document order, starting at `1`. The `<conjunctionExpression>` uses those numbers in prefix notation.

For six conditions grouped as two entity-type checks, two principal checks, and two tag checks:

```xml
<conjunctionExpression>(AND (OR 1 2) (AND 3 4) (AND 5 6))</conjunctionExpression>
```

**Top-level operator must always be `AND`.** Never emit a bare top-level `(OR 1 2)` — the UI treats it as `// ERROR: Unsupported rule!` and silently drops the rule — and never emit a bare top-level condition index (e.g. `3` instead of `(AND 3)`), which crashes the builder. `OR` is allowed only inside a single section's local group, never as (or at) the top level. Wrap every local group under a top-level `AND`: `(AND (OR 1 2))`, `(AND 3)`. See `ui-compatibility.md` for the full non-round-trip checklist.

Construction:

1. Number every `<conditions>` element from top to bottom.
2. Build each local group using those numbers.
3. Combine the groups with the top-level `AND` operator — never a bare top-level `OR` or a bare index.
4. Check that every referenced number exists exactly once in the intended expression.

Do not renumber conditions after changing their order without updating the expression.

An `EXISTS` resource expression can contain nested `policyRuleDefinitionCondition` elements. Its `whereClauseConjunction` has a separate one-indexed namespace. For one nested condition, use `<whereClauseConjunction>1</whereClauseConjunction>` exactly as preserved by the semantic `ExistsJoinRLS` example.
