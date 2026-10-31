# Conjunction Compiler

Construct conjunctions from a typed intermediate plan, not by hand-editing an expression string.

1. Build and validate all conditions.
2. Classify each condition into `DATA_SPACE`, `TAG_CLASSIFICATION`, `PERMISSION`, `ENTITY_TYPE`, or `RECORD_FIELD`; never mix classifications, permissions, entity types, and RLS criteria in one local group.
3. Reject conditions that cannot belong to a selected consumer/profile.
4. Assign stable condition IDs after final ordering.
5. Build each non-empty local group with its requested operator.
6. In normal author mode for `DATACLOUD`, build a typed custom-conjunction plan for UI validation, then serialize it to the ordinary MDAPI `conjunctionExpression`. There is no literal `CUSTOM` XML element. For example, two alternative classifications plus one required permission become `(AND (OR 1 2) (AND 3))`.
7. For `ALL`, use the general conjunction contract.
8. Validate that every condition is referenced exactly once, no unknown ID is referenced, no group is empty, and nested RLS join conditions use independent numbering.

In explicit evidence-recreation mode, do not compile or normalize the named API 69.0 example's conjunction. Its exact condition order and conjunction take precedence; validate their internal index consistency and reproduce them verbatim.

For `DATACLOUD`, a typical OLS tree is:

```text
CUSTOM(AND,
  ENTITY_TYPE(OR, 1, 2),
  TAG_CLASSIFICATION(OR, 3, 4),
  PERMISSION(AND, 5))
```

The XML has no literal section elements; section identity is represented by the custom-conjunction tree consumed by the UI.
