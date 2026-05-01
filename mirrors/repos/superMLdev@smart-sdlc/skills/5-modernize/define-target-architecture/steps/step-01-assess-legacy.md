# Step 01 — Assess Legacy System for Architecture Replacement

**Previous step:** (activation)
**Next step:** `step-02-capture-tech-framework.md`

---

## Goal

Produce a clear profile of what the legacy system does, organized by component type. This drives architecture decisions in step 3.

---

## 1. Read Legacy Profile

Load from previously built artifacts:
- `_superml/legacy-inventory/programs.md`
- `_superml/legacy-inventory/data-dictionary.md`
- `_superml/legacy-inventory/job-flows.md`
- `_superml/legacy-inventory/integrations.md`
- `_superml/knowledge-graph/process-flows.md`
- `_superml/business-rules/validated-rules.md`

---

## 2. Classify Legacy Components by Replacement Type

For each legacy component, determine what modern architectural pattern it maps to:

### Batch Processing → Event/Service

```
Legacy: JCL job ORDVALD (validates 50K orders nightly)
What it does: Validation batch — processes orders from file
Modern equivalent options:
  Option A: Synchronous API call (validate at order placement time)
  Option B: Async message processing (order placed → validation event → result event)
  Option C: Scheduled batch retained (if business requires nightly cycle)
Recommended: Option A (if order count allows real-time) or B (if volume is high)
Note: Business rule RULE-005 requires validation before posting — must be enforced
```

### CICS Online Screens → API + UI

```
Legacy: CICS transaction ORDE / ORDMAP (BMS map)
What it does: Green-screen order entry for CSRs
Modern equivalent: REST API (backend) + Web UI or Mobile (frontend)
Data model: Order creation endpoint POST /orders
Screen fields → API request body fields
CICS COMMAREA → session state (stateless API + JWT)
```

### DB2 / VSAM Files → Database

```
Legacy: DB2 tables (CUSTOMER, ORDERS, PRODUCTS) + VSAM KSDS (CUSTMSTR)
What they store: Master data
Modern equivalent options:
  Option A: Relational DB (same structure, cleaner schema)
  Option B: NoSQL (for high-volume lookups — e.g., product catalog)
  Option C: Hybrid (relational for transactional + cache for reads)
Recommendation: Relational first (schema is well-defined, business rules are relational)
Note: VSAM KSDS → keyed relational table (direct mapping)
```

### External File Interfaces → Integration Layer

```
Legacy: Batch file exchange with GL system (GL.ENTRIES.FILE)
Modern equivalent:
  Option A: REST API call to GL system (if GL has been modernized)
  Option B: Message queue → GL system subscribes
  Option C: Retain file exchange (if GL cannot change)
Question for user: Has the external GL system been modernized? Does it have an API?
```

### Shared Subprograms → Microservice / Library

```
Legacy: TAXCALC called by 7 programs
Modern equivalent:
  Option A: Shared library (if all callers in same service)
  Option B: Tax calculation microservice (if callers will be separate services)
  Option C: Third-party tax service (if tax rules are standard enough)
```

---

## 3. Legacy Risk Assessment

Assess each component area for migration risk:

```
Component Risk Assessment:

HIGH RISK — complex business logic, many rules, many dependencies:
  - ORDVALD: 45 business rules, called by 7 programs, integrates with 3 external systems
  - TAXCALC: Tax rules vary by jurisdiction — needs careful rule extraction

MEDIUM RISK — moderate complexity, some external dependencies:
  - CUSTMGMT: Clear CRUD operations but has audit requirements (RULE-019)
  - INVUPD: Concurrency concerns — multiple jobs can update same record

LOW RISK — simple, well-understood, few dependencies:
  - RPTGEN: Report generation — can be replaced independently
  - CUSTINQ: Read-only inquiry — safe to replace first
  - ERRHAND: Error handling utility — replace with framework-level handler
```

---

## 4. Legacy-to-Modern Mapping Summary

Write to screen as a summary table:

```
Legacy Component Replacement Map:
══════════════════════════════════════════════════════════

TYPE: Batch Processing ({n} jobs)
  ORDPROC chain     → Order Processing Service (async/event-driven)
  MONTHEND          → Scheduled Job Service (keep batch pattern)
  RPTGEN            → Report Service or BI tool
  
TYPE: Online Screens ({n} CICS transactions)
  ORDE (Order Entry) → POST /api/orders
  CUSTE (Customer)   → GET/PUT /api/customers
  ORDI (Inquiry)     → GET /api/orders/{id}
  MENU              → Frontend navigation (no backend equivalent)

TYPE: Data Storage ({n} tables + VSAM)
  CUSTOMER (DB2)    → customers table (relational)
  ORDERS (DB2)      → orders table (relational)
  CUSTMSTR (VSAM)   → Merge into customers table (VSAM was a cache)
  
TYPE: Business Logic Programs ({n} subprograms)
  TAXCALC           → Tax Service or library
  CUSTINQ           → Customer Service — query layer
  PRICEINQ          → Product/Pricing Service

TYPE: External Integrations ({n})
  GL file exchange  → [VERIFY: does GL system have API now?]
  EDI output        → EDI adapter (or third-party EDI service)
  Order input file  → [VERIFY: can order source system send events instead?]

HIGH RISK items requiring careful migration planning:
  1. ORDVALD — 45 rules, high volume, core business process
  2. TAXCALC — tax jurisdiction complexity
  3. CUSTMSTR VSAM → DB migration (data transformation needed)
══════════════════════════════════════════════════════════
```

---

## 5. Data Migration Complexity

Assess data migration needs:

```
Data Migration Assessment:
  
  CUSTMSTR (VSAM KSDS):
    Records: {n estimated}
    Format change: Binary COBOL fields → standard SQL types
    Complexity: MEDIUM — field-by-field conversion needed, PIC S9 → decimal
    Showstopper: REDEFINES fields ({n} found) — need business rule to resolve
    
  ORDERS (DB2):
    Records: {n estimated}
    Format change: Minor — already relational
    Complexity: LOW — standard SQL export/import
    
  Archive data: Does it need to migrate? [{n} years of history} — confirm with user
```

⏸️ **STOP** — Present the legacy-to-modern mapping. Ask:
1. "Are there components you see here that should NOT be modernized? (e.g., scheduled to be decommissioned)"
2. "Are there components not listed that need to be included?"
3. "For HIGH RISK items — are there any additional constraints I should know about?"
4. "For external integrations — which external systems have already been modernized and have APIs?"

---

## Save State

Update `{project-root}/_superml/modernize-state.yml`:
```yaml
step: "arch-step-01-assess-legacy"
status: "complete"
components_mapped: {n}
high_risk_components: {n}
data_migration_complexity: {Low|Medium|High}
external_systems_needing_verification: {n}
```

Load and follow `./step-02-capture-tech-framework.md`.
