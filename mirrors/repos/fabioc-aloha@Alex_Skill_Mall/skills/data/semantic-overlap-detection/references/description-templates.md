# Description Templates

Standard phrasing templates for TMDL column descriptions (`///` comments). Each template follows the **IS / IS NOT / CANONICAL** pattern. Replace `{placeholders}` with model-specific values.

## The IS / IS NOT / CANONICAL Pattern

Every disambiguation-critical column description should contain three elements:

1. **IS**: What classification system this column belongs to, its granularity level, and example values
2. **IS NOT**: Which competing column(s) the user might confuse it with, and how they differ
3. **CANONICAL**: Whether this is the preferred column for its domain, or which column to prefer instead

Keep descriptions under 3 lines — Copilot performs better with concise descriptions.

---

## Template 1: Canonical Column

Use when this column is the primary/preferred column for its domain.

```
/// {What it is} ({example values}).
/// Primary column for {domain} analysis.
/// NOT {competing column} on {competing table} ({what that column is instead}).
```

## Template 2: Secondary Column

Use when another column is canonical and this one should rarely be the first choice.

```
/// {What it is} ({example values}).
/// This is a {what makes it different} classification. NOT {what users probably mean}.
/// For {typical user intent}, use {canonical column} on {canonical table} instead.
```

## Template 3: Cross-Table Duplicate (Class D)

Use when the same column exists on a secondary table via a different join/security path.

```
/// {What it is} ({access path description}).
/// Same data as {canonical table}.{column} but via a different {bridge/security} path.
/// Prefer {canonical table} for standard queries.
```

## Template 4: Hierarchy Level Column (Class B)

Use when the column is one of multiple granularity levels for the same attribute.

```
/// {Granularity level} of {attribute} ({example values}).
/// {Relationship to other levels}: more granular than {parent}, less granular than {child}.
/// Use for {when to use this level}. For {other use case}, use {other column}.
```

## Template 5: Redundant Numeric Column (Class B)

Use when a column duplicates another in a different format (numeric, sortable, etc.).

```
/// Numeric/sortable representation of {source column}. Contains the same values.
/// For filtering and analysis, prefer {source column} (the primary column).
```

## Template 5b: Excluded Column with Preferred Alternative

Use when a column is being excluded from the AI data schema but should still have a description for documentation. Choose the "prefer X instead" phrasing based on the ambiguity class.

```
/// {What it is} — {format or purpose} representation of {root concept}.
/// Excluded from AI schema. For {typical user intent}, prefer {canonical column} on {table}.
```

## Template 6: Entity-Level vs Unit-Level (Class A)

Use when a column classifies the organizational unit, NOT the entity directly. This template uses 3 lines — condense the divergence example into the IS NOT line if needed.

```
/// {What it classifies} for the {unit type} ({example values}).
/// Classifies the {UNIT}, NOT the {entity}. {Concrete divergence example}.
/// For {entity}-level {domain}, use {entity column} on {entity table}.
```

## Template 7: Collision-Prone Column (Class A)

Use when a geographic or naming value collides with a different-scope interpretation.

```
/// {What it is} ({example values}).
/// "{collision value}" here means {this interpretation}, NOT {other interpretation}.
/// For {other interpretation}, use {other column} instead.
```

## Template 8: Legal/Jurisdictional Column

Use when a column represents legal/contractual entity rather than physical location.

```
/// {Jurisdictional classification} — {what relationship it represents} ({example values}).
/// {How it can diverge from physical attributes}.
/// Use for {legal/entity use case}. For {physical use case}, use {alternative column}.
```

---

## Applying Templates

1. Identify which ambiguity class applies to the column (see [ambiguity-classes.md](./ambiguity-classes.md))
2. Select the matching template
3. Fill in placeholders with actual model values — use real column names and realistic example values from the model
4. Place the `///` comment immediately before the `column` keyword in the TMDL file
5. Multiple `///` lines concatenate into a single description

## Quality Checklist

Before finalizing a description, verify:

- [ ] The description names at least one competing column by its exact `Table.Column` name
- [ ] Example values are real values from the model, not hypothetical
- [ ] The "NOT" clause explains WHY it's different, not just that it IS different
- [ ] The canonical column recommendation matches the domain's canonical column table from the analysis
- [ ] The description is ≤3 lines — longer descriptions dilute the signal
