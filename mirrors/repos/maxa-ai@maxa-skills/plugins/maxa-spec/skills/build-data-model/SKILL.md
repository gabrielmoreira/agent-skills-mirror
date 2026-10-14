---
name: build-data-model
description: >-
  Use only when the project contains a Maxa AI Specification (a folder
  with `maxa-spec.yaml`, or `project.yaml` declaring
  `bundle_format_version`), or when the user mentions a Maxa spec.
  Build data models, write SQL/dbt transforms, or implement KPIs using
  the Maxa AI Specification. Use when designing entity schemas,
  writing transforms, implementing financial calculations, or building
  a data pipeline grounded in business discovery output. Also use when
  the user asks to create staging/intermediate/mart layers, implement
  a Kimball/Medallion/Data Vault/OBT architecture, or write code that
  references entities, business rules, or KPIs from the Maxa spec.
---

# Build Data Model

You are a data engineer building a data model grounded in a Maxa AI Specification. The specification contains structured business understanding — entities, attributes, business rules, KPIs, source-system conventions, and computation recipes — extracted from real stakeholder discovery. Your job is to activate this knowledge at every code decision point.

## Step 0: Locate the Maxa spec

Search the project for the Maxa AI Specification in this order, and stop at the first step that finds one:

1. `maxa-spec.yaml`: `find . -name maxa-spec.yaml -not -path '*/node_modules/*' -not -path '*/.git/*'`. The directory containing it is the specification root.
2. `project.yaml` declaring `bundle_format_version` (older format): `find . -name project.yaml -not -path '*/node_modules/*' -not -path '*/.git/*'`, then keep only the files that contain `bundle_format_version`. The directory containing it is the specification root.
3. An `./ai-specification/` or `./project/ai-specification/` folder
4. A `./business-knowledge-bundle/` or `./project/business-knowledge-bundle/` folder
5. If none of these finds a Maxa spec, ask the user where it is. Don't assume another folder holds a Maxa spec because of its name.

If a step finds more than one Maxa spec, ask the user which one to use.

Read `index.md` from the specification root to understand available content.

Remember the specification root path — every file reference below is relative to it.

## Step 1: Read the index

Read `index.md` from the specification root. This is your table of contents. It lists every entity, KPI category, theme, and reference file with one-line descriptions. Use it to understand what's available before reading individual files.

Do NOT read the entire specification at once. Read only what's relevant to the current task. For broad tasks like "build the entire star schema," reading all entity files is expected — the routing table below still applies for theme and reference files.

## Step 2: Route to the right specification files

Based on what you're building, read the relevant files:

| Working on | Read these specification files |
|---|---|
| Entity schemas / table design | Entity files in `entities/`, `modeling-decisions.md`, `scope-map.md` |
| SQL transforms / KPI implementation | `specialized-instructions.md` (computation recipes section), relevant entity files |
| Revenue, cost, or P&L logic | `themes/financial-processes.md`, `kpis/financial-kpis.md` |
| Operational metrics | `themes/operational-processes.md`, `kpis/operational-kpis.md` |
| Source-to-target mapping | `themes/source-systems.md`, `reference/entity-examples.md` |
| Data type or format handling | Entity files (Data Conventions sections), `specialized-instructions.md` (Implementation Checklist section) |
| Scope or requirements questions | `themes/project-scope.md`, `themes/use-cases.md` |
| Industry or business context | `themes/business-domain.md` |
| Validation values | `reference/numerical-examples.md`, `reference/business-questions.md` |
| Unknowns or gaps | `known-gaps.md`, `follow-up-questions.md`, `expert-observations.md` |

When multiple areas apply, read all relevant files. If unsure whether a theme file is relevant, check its one-line description in `index.md` before loading it.

## Step 3: Apply business rules — flag gaps proactively

Every entity file contains a "Business Rules Affecting This Entity" section. These rules use RFC 2119 vocabulary — [MUST], [MUST NOT], [SHOULD] — to indicate binding requirements vs recommendations.

Whenever you build or modify anything related to an entity:

1. Read that entity's Business Rules section
2. For each rule, check whether your current output addresses it
3. **Proactively flag any rule not yet addressed** — do not silently proceed. State which rule, what it requires, and what's missing in your implementation
4. Rules marked [MUST] are non-negotiable. Rules marked [SHOULD] can be deferred with justification

This check runs fresh every time you touch an entity — there is no separate checklist to track. The entity file IS the checklist.

## Step 4: Run checks against the Implementation Checklist before finalizing transforms

`specialized-instructions.md` contains an Implementation Checklist section organized by entity. Older Maxa specs title this section "Pre-Flight Checklist" — treat both headings as the same section. Before finalizing any transform or model:

1. Read the Implementation Checklist for every entity your code touches
2. Verify each item against your implementation
3. Flag any item that is not satisfied — do not proceed without acknowledging it

Common checklist items include data type conversions (European comma decimals, BIGINT dates, VARCHAR amounts), sentinel value handling (the # hash value is a legitimate dimension member), leaf-vs-rollup account filtering, and version field filtering.

## Step 5: Use entity relationship patterns for joins

`specialized-instructions.md` contains an Entity Relationship Patterns section. When writing joins between entities:

1. Read the relevant relationship pattern
2. Use the documented join keys — do not guess column names
3. Respect the documented cardinality and constraints
4. Apply any business constraints noted in the pattern (e.g., "operating expense transactions use customer_id = '#'")

## Step 6: Validate with reference data

Before declaring your model complete:

1. Read `reference/numerical-examples.md` — check that your model can reproduce the documented values
2. Read `reference/business-questions.md` — verify your model can answer the validated business questions
3. If a value doesn't match, trace the discrepancy through the computation recipe in `specialized-instructions.md`
