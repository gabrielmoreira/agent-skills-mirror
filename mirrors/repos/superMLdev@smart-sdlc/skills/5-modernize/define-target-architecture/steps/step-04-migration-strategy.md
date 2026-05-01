# Step 04 — Migration Strategy

**Previous step:** `step-03-design-architecture.md`
**Next step:** create-migration-epics (next skill)

---

## The Three Migration Approaches

Before recommending an approach, Rex explains the options:

```
🏛️ There are three ways to migrate a legacy system. I'll recommend one based on your system profile, but the decision is yours.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
APPROACH A — Strangler Fig (RECOMMENDED for most cases)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Route new traffic to new system component by component.
Legacy system continues to run for un-migrated parts.

✅ Pros: Low risk, continuous delivery, easy rollback per component
✅ Safe: Old system is always available as fallback
⚠️ Cons: Two systems running in parallel = data sync complexity
⚠️ Duration: 12–24 months for enterprise systems

Best for: Large systems, high business criticality, risk-averse organization

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
APPROACH B — Parallel Run
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Run old and new system simultaneously. Compare outputs.
Go-live only when new system matches old system exactly.

✅ Pros: Highest validation confidence — you KNOW the new system is correct
⚠️ Cons: Double the operational cost, complex comparison logic
⚠️ Duration: 6–18 months

Best for: Financial systems, regulated industries, zero-tolerance for errors

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
APPROACH C — Big Bang
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Migrate everything at once. Go-live on a single cutover date.

⚠️ HIGH RISK: If anything goes wrong, rollback is extremely difficult
✅ Pros: No parallel operation complexity, clean break
✅ Cons: All-or-nothing — requires perfect testing before go-live

Best for: Small systems only, or when the legacy system CANNOT continue to run

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Recommendation Based on System Profile

```
Based on your system profile:
  Programs: {n}
  Business rules: {n}
  External integrations: {n}
  Data volume: {estimated}
  Business criticality: {inferred}

MY RECOMMENDATION: {A|B|C} — {reason}

Factors in this recommendation:
  - {reason 1}
  - {reason 2}
  - {reason 3}
```

Ask:
> "Do you agree with this approach, or would you like to use a different strategy? This decision will shape the entire migration plan."

---

## Strangler Fig Migration Phases (if Approach A selected)

Define migration phases based on risk and dependency order:

### Phase 0 — Foundation (not visible to users)
```
Duration: 4–6 weeks
Goal: Infrastructure in place, development environment ready, no business functionality yet

Tasks:
  - Cloud infrastructure provisioned (Terraform/IaC)
  - CI/CD pipeline operational
  - Kubernetes cluster running
  - Shared services: Auth (OAuth2 provider), API Gateway, Logging, Secrets management
  - Database clusters provisioned (not yet populated)
  - Kafka/messaging infrastructure (if async)
  - Development standards documented and team trained

Success criteria: A "Hello World" service deployed to production infrastructure
```

### Phase 1 — Low-Risk Components First (Strangler Fig entry point)
```
Duration: 6–8 weeks
Goal: First real business functionality in new system — choose lowest risk component

Recommended starting point: {lowest risk component from Step 01 assessment}
  (Often: Customer Inquiry, Product Catalog, or Report Generation)

Why start here:
  - Read-only or low-stakes functionality
  - If it fails, users can fall back to legacy with no data impact
  - Team learns the new tech stack on a low-risk component
  
Steps:
  1. Build {component} in new system
  2. Route new system URL alongside legacy (both available)
  3. Pilot with small user group
  4. Full cutover — retire legacy {component}
```

### Phase 2 — Core Domain Migration
```
Duration: {estimated based on complexity}
Goal: Core business entities and their write operations

Order: From lowest dependency count to highest
  Phase 2a: Customer Management (Service A)
  Phase 2b: Product/Pricing (Service B — depends on nothing in new system)
  Phase 2c: Order Entry (Service C — depends on 2a + 2b being in new system)
  
Data sync: While strangling, new system reads from BOTH sources
  - Customer data: New system is authoritative for new customers
  - Old customers: Still in legacy DB, read via data sync API or direct read
```

### Phase 3 — Batch Processing Migration
```
Duration: 4–8 weeks
Goal: Replace nightly batch jobs with event-driven processing

Approach: Shadow mode first
  1. Run new event-driven processing alongside legacy batch
  2. Compare outputs for 2–4 weeks
  3. Validate all business rules produce identical results
  4. Disable legacy batch — new system is authoritative

Risk mitigation: Keep legacy batch code archived for 6 months post-migration
```

### Phase 4 — Integration Cutover
```
Duration: 4–6 weeks
Goal: External systems now connect to new system

Steps:
  1. GL integration: Migrate file exchange to API/event (if GL system ready)
  2. EDI output: New EDI adapter deployed
  3. Order input: Source system redirected to new Order API
  
Note: External system changes may require external project coordination
```

### Phase 5 — Decommission Legacy
```
Duration: 2–4 weeks
Goal: Legacy system fully retired

Prerequisites:
  - All data migrated and verified
  - All functionality verified in new system for minimum 30 days
  - Rollback plan documented but unused
  - All integrations confirmed on new system
  - Business sign-off received
  
Steps:
  1. Freeze legacy system (read-only, no new data)
  2. Final data sync from legacy → new system
  3. 30-day observation period
  4. Decommission legacy infrastructure
  5. Archive legacy source code in version control (never delete)
```

---

## High-Risk Areas and Mitigation

```
HIGH RISK AREAS identified:

1. ORDVALD — 45 business rules, high volume
   Risk: New system misses a business rule → orders processed incorrectly
   Mitigation: Parallel Run for this component specifically (2-3 months)
   Success criteria: New system and legacy produce identical results for 1M orders

2. Data Migration — VSAM binary format
   Risk: Data corruption during conversion
   Mitigation: Conversion script + automated reconciliation report
   Success criteria: Record count matches + financial totals match to the cent

3. Tax Calculation — jurisdiction complexity
   Risk: Tax calculated incorrectly → regulatory exposure
   Mitigation: Consider third-party tax service; exhaustive test cases from tax team
   
4. External Integrations — GL system
   Risk: GL system not ready for API integration
   Mitigation: Keep file exchange as fallback; build adapter that supports both
```

---

## Write Migration Strategy Document

Write `{project-root}/_superml/modernization/MIGRATION_STRATEGY.md`:

```markdown
# Migration Strategy — {project_name}

## Approach: {Strangler Fig | Parallel Run | Big Bang}
**Decision rationale:** {reason}
**Decision made by:** {role}
**Date:** {date}

## Migration Phases

### Phase 0 — Foundation ({duration})
{...}

### Phase 1 — {name} ({duration})
{...}

### Phase 2 — {name} ({duration})
{...}

## Timeline (estimated)
| Phase | Start | Duration | Milestone |
|-------|-------|----------|-----------|
| 0 — Foundation | Month 1 | 6 weeks | Infrastructure ready |
| 1 — Read-only services | Month 2 | 8 weeks | First production service live |
| 2a — Customer | Month 4 | 6 weeks | Customer service live |
| 2b — Product/Pricing | Month 5 | 4 weeks | Product service live |
| 2c — Order Entry | Month 6 | 8 weeks | Order entry live in new system |
| 3 — Batch migration | Month 8 | 8 weeks | Batch processing in new system |
| 4 — Integrations | Month 10 | 6 weeks | All external connections migrated |
| 5 — Decommission | Month 12 | 4 weeks | Legacy retired |

## Risk Register
| Risk | Severity | Mitigation | Owner |
|------|----------|-----------|-------|
| Business rule missed | HIGH | Parallel run for order processing | Tech Lead |
| Data corruption in migration | HIGH | Automated reconciliation | Data Team |
| Tax errors | HIGH | Tax team validation + third-party service | Compliance |

## Go-Live Checklist (per component)
- [ ] All business rules for this component verified in new system
- [ ] Performance tested to {n} transactions/second
- [ ] Rollback procedure documented and tested
- [ ] Monitoring and alerting configured
- [ ] Business owner sign-off received
```

---

## Present Strategy Summary

```
🏛️ Architecture and Migration Strategy Complete
══════════════════════════════════════════════════════════

Migration approach: {Strangler Fig}
Estimated duration: {n} months
Migration phases: {n}

Documents written:
  ✅ _superml/modernization/tech-framework.md
  ✅ _superml/modernization/target-architecture.md
  ✅ _superml/modernization/architecture-diagram.mmd
  ✅ _superml/modernization/MIGRATION_STRATEGY.md

Services in new architecture: {n}
APIs designed: {n}
Business rules traceable: {n}/{total}

High-risk items requiring special attention: {n}

══════════════════════════════════════════════════════════
Ready for: create-migration-epics
  → Convert architecture + migration phases into implementable epics and stories
```

⏸️ **STOP** — Confirm strategy before proceeding to epics.

---

## Save State

Update `{project-root}/_superml/modernize-state.yml`:
```yaml
step: "arch-step-04-migration-strategy"
status: "complete"
migration_approach: "{strangler-fig|parallel-run|big-bang}"
migration_phases: {n}
estimated_duration_months: {n}
ready_for: "create-migration-epics"
```
