# create-migration-epics

> Convert the modernization architecture and migration strategy into implementable epics and tech stories — traceable to validated business rules and legacy source programs.

## Purpose

This skill bridges architecture and implementation. It takes the outputs of:
- `define-target-architecture` — what to build
- `validate-business-rules` — what rules to enforce
- `MIGRATION_STRATEGY.md` — in what order to build it

And produces a structured epic/story breakdown compatible with the existing `create-epics-stories` skill format — but with migration-specific story types: data migration, rule re-implementation, integration cutover, and legacy retirement.

## Persona

This skill is executed by **Leo** (Product Manager) working closely with Rex (Architecture context) and Aria (Business rules context).

## Prerequisites

All of these should exist before running:
- `_superml/modernization/target-architecture.md`
- `_superml/modernization/MIGRATION_STRATEGY.md`
- `_superml/business-rules/validated-rules.md`
- `_superml/knowledge-graph/process-flows.md`

## Activation

> "I'm Leo — I'll turn your modernization architecture into implementable epics and stories.
> Each story will be traceable to:
>   - The business rule(s) it implements
>   - The legacy program(s) it replaces
>   - The migration phase it belongs to
>
> How would you like stories formatted?
> 1. Gherkin (Given/When/Then) — good for BDD teams
> 2. Standard (As a / I want / So that) — classic user story
> 3. Technical (Title + Acceptance Criteria numbered list)
> 4. Mix — user stories for functional work, technical format for infra/migration tasks"

---

## Epic Structure for Modernization

### Standard Epic Categories (always present)

```
EPIC-M01: Platform Foundation
  Everything needed before the first business service can be built.
  Stories: Infrastructure, CI/CD, Shared services, Developer environment.

EPIC-M02: Data Migration
  Moving legacy data to new schema. One story per entity.
  Stories: Schema migration script, Data extraction, Transformation, Validation/reconciliation.

EPIC-M{n}: {Domain} Service — one epic per service
  Building the new service for each domain.
  Stories: API endpoints, Business rule implementation, Database layer, Tests.

EPIC-M{n+1}: Integration Cutover
  Switching external systems to the new system.
  Stories: One per external integration.

EPIC-M{n+2}: Legacy Retirement
  Decommissioning the legacy components.
  Stories: Traffic cutover, Parallel run observation, Decommission.

EPIC-M{n+3}: Post-Migration Validation
  Verifying the new system is correct.
  Stories: Business rule verification, Performance baseline, User acceptance.
```

---

## Story Generation

### For Each Service (e.g., Customer Service)

Generate stories covering:

#### API Endpoint Stories
```
Story: Create customer profile API
  As a Customer Service Representative
  I want to create a new customer profile via the API
  So that new customers can start placing orders

  Acceptance Criteria:
  - POST /api/v1/customers accepts customer data
  - Returns 201 Created with customerId on success
  - Returns 422 with field errors if validation fails
  - Customer is created in Active status (RULE-002)
  - Duplicate customer ID rejected with 409 Conflict
  
  Business rules implemented: RULE-002
  Legacy program replaced: CUSTMAINT.cbl (create path)
  Migration phase: Phase 2a
  Story points: {estimate}
```

#### Business Rule Implementation Stories
For each business rule, if it's non-trivial (more than a simple field validation), it gets its own story:

```
Story: Implement credit limit enforcement (RULE-001)
  As a developer implementing the Order Service
  I want to enforce credit limit validation at order placement
  So that customers cannot exceed their credit limit

  Technical specification:
  - On POST /orders, before creating order:
    1. Fetch customer.creditLimit and customer.currentBalance
    2. If (order.total + customer.currentBalance) > customer.creditLimit: return 422
    3. Error response must include: currentBalance, creditLimit, orderTotal, shortfall
  - Credit check must be consistent-read (not cached) to prevent race conditions
  - Unit test: 5 scenarios (under limit, at limit, over limit, zero limit, negative balance)
  - Integration test: verify rejection message matches RULE-001 specification

  Business rules implemented: RULE-001
  Legacy program replaced: ORDVALD.cbl paragraph 0210-CHECK-CREDIT-LIMIT
  Migration phase: Phase 2c
```

#### Data Migration Stories
```
Story: Migrate customer records from VSAM to PostgreSQL
  
  Technical specification:
  - Source: VSAM KSDS CUSTMSTR.KSDS (n records estimated)
  - Target: PostgreSQL customers table
  - Conversion required:
    * PIC 9(8) CUST-ID → CHAR(8) id
    * PIC S9(7)V99 CUST-CREDIT-LIMIT → DECIMAL(9,2) credit_limit
    * PIC X(1) CUST-STATUS (A/S/C) → VARCHAR(1) status with CHECK constraint
  - Validation:
    * Record count in source = record count in target
    * Sum of credit_limit matches within $0.01 (rounding tolerance)
    * All status values are valid (A/S/C only — reject and report any unknown)
    * Zero CUST-ID records rejected (data quality gate)
  - Output: Migration report showing records migrated, rejected, warnings
  
  Business rules preserved: RULE-002 (status constraint enforced in schema)
  Legacy source: CUSTMSTR.KSDS
  Migration phase: Phase 2a
```

#### Integration Stories
```
Story: Implement GL accounting entry event publisher
  
  As a financial systems integrator
  I want the Order Service to publish accounting events
  So that the General Ledger system receives entries without file exchange

  Technical specification:
  - When Order status changes to Confirmed: publish AccountingEntryRequired event
  - Event payload: { orderId, customerId, amount, glAccount, timestamp }
  - Kafka topic: accounting-entries
  - If GL system is not yet on events: GL Integration Service reads Kafka → writes file
    (adapter pattern — supports both old and new GL integration)
  
  Legacy program replaced: ACCTPOST.cbl + GL.ENTRIES.FILE production
  Migration phase: Phase 4
```

---

## Story Traceability Matrix

Write `{project-root}/_superml/modernization/story-traceability.md`:

```markdown
# Story Traceability Matrix

This matrix links every implementation story to its business rules and legacy source.
No story should be delivered that isn't traceable to at least one business rule OR
one legacy component being replaced.

| Story | Epic | Business Rules | Legacy Replaced | Phase |
|-------|------|---------------|----------------|-------|
| Create customer API | EPIC-M03 | RULE-002 | CUSTMAINT.cbl (create) | 2a |
| Credit limit enforcement | EPIC-M04 | RULE-001 | ORDVALD.cbl:0210 | 2c |
| Migrate customer data | EPIC-M02 | RULE-002 | CUSTMSTR.KSDS | 2a |
| ... | | | | |

## Business Rules Coverage

Every validated business rule must appear in at least one story.
Rules not yet in any story:
  - RULE-{n}: {rule statement} → needs story in {epic}
```

---

## Output

Write `{project-root}/_superml/modernization/epics-and-stories.md` with the full breakdown.

Present completion summary:

```
🏛️ Migration Epics Complete — {project_name}
══════════════════════════════════════════════

Epics created: {n}
Stories created: {n}

By type:
  Platform/Infrastructure: {n} stories
  Data Migration:          {n} stories
  Service Implementation:  {n} stories
  Business Rule stories:   {n} stories  (one per complex rule)
  Integration stories:     {n} stories
  Retirement stories:      {n} stories

By migration phase:
  Phase 0 (Foundation):   {n} stories
  Phase 1 (First service): {n} stories
  Phase 2 (Core domain):  {n} stories
  Phase 3 (Batch):        {n} stories
  Phase 4 (Integration):  {n} stories
  Phase 5 (Decommission): {n} stories

Business rule coverage: {n}/{total} rules have at least one story
Uncovered rules: {n} — stories to be added

Files written:
  ✅ _superml/modernization/epics-and-stories.md
  ✅ _superml/modernization/story-traceability.md

══════════════════════════════════════════════
Modernization pipeline complete!

The full pipeline output is in:
  _superml/legacy-inventory/     — What the old system does
  _superml/knowledge-graph/      — Domain model and business rules
  _superml/business-rules/       — Validated BA-reviewed rules
  _superml/modernization/        — Architecture + migration plan + stories

Next: Load stories into your backlog tool, or use the JIRA integration to push epics.
```

## Integration with Other Skills

- Stories are compatible with the `create-epics-stories` story format
- Can be pushed to JIRA using the `integrations/jira` skills
- Architecture ADRs compatible with `integrations/confluence` for documentation
- Stories are implementation-ready for Nova (phase 4 — `dev-story` skill)
