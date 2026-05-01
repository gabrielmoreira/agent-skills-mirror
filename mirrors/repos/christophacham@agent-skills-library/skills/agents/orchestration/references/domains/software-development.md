# Software Development Orchestration Patterns

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   Building software is what we do best.                     │
│   Features, fixes, refactors — all orchestrated elegantly.  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

> **Load when**: Feature implementation, bug fixes, refactoring, migrations, greenfield development
> **Common patterns**: Plan-Parallel-Integrate, Diagnose-Hypothesize-Fix, Map-Analyze-Transform

## Table of Contents

1. [Feature Implementation](#feature-implementation)
2. [Bug Fixing](#bug-fixing)
3. [Refactoring](#refactoring)
4. [Migration](#migration)
5. [Greenfield Development](#greenfield-development)

---

## Feature Implementation

### Pattern: Plan-Parallel-Integrate

```
User Request: "Add user authentication"

Phase 1: PIPELINE (Research → Plan)
├─ Explore agent: Find existing auth patterns, user models, middleware
└─ Plan agent: Design auth architecture using findings

Phase 2: FAN-OUT (Parallel Implementation)
├─ Agent A: Implement user model + database schema
├─ Agent B: Implement JWT/session middleware
├─ Agent C: Implement login/logout routes
└─ Agent D: Implement frontend auth components

Phase 3: PIPELINE (Integration)
└─ General-purpose agent: Wire components, add tests, verify flow
```

**Task breakdown with cc-mirror tasks:**

```bash
npx cc-mirror tasks create --subject "Design authentication architecture" --description "Plan JWT flow, middleware structure"
npx cc-mirror tasks create --subject "Implement user model and schema" --description "Database schema, validation"
npx cc-mirror tasks create --subject "Build auth middleware" --description "JWT verification, route protection"
npx cc-mirror tasks create --subject "Create auth API routes" --description "Login, logout, register endpoints"
npx cc-mirror tasks create --subject "Build frontend auth UI" --description "Login form, protected routes"
npx cc-mirror tasks create --subject "Integration testing" --description "End-to-end auth flow tests"

# Dependencies
npx cc-mirror tasks update 2 --add-blocked-by 1
npx cc-mirror tasks update 3 --add-blocked-by 1
npx cc-mirror tasks update 4 --add-blocked-by 1
npx cc-mirror tasks update 5 --add-blocked-by 1
npx cc-mirror tasks update 6 --add-blocked-by 2,3,4,5
```

### Pattern: Vertical Slice

For full-stack features, implement one complete slice first:

```
Phase 1: Single complete flow
└─ General-purpose agent: DB → API → UI for one use case

Phase 2: FAN-OUT expansion
├─ Agent A: Additional DB operations
├─ Agent B: Additional API endpoints
└─ Agent C: Additional UI components
```

---

## Bug Fixing

### Pattern: Diagnose-Hypothesize-Fix

```
User Request: "Users can't log in after password reset"

Phase 1: FAN-OUT (Parallel Diagnosis)
├─ Explore agent: Search error logs, recent changes to auth
├─ Explore agent: Find password reset flow implementation
└─ Explore agent: Check session/token handling

Phase 2: PIPELINE (Analysis)
└─ General-purpose agent: Synthesize findings, form hypotheses

Phase 3: SPECULATIVE (If cause unclear)
├─ Agent A: Test hypothesis 1 (token expiry issue)
├─ Agent B: Test hypothesis 2 (session invalidation)
└─ Agent C: Test hypothesis 3 (password hash mismatch)

Phase 4: PIPELINE
└─ General-purpose agent: Implement fix, add regression test
```

### Pattern: Reproduction-First

```
Phase 1: Reproduce
└─ General-purpose agent: Create minimal reproduction case

Phase 2: Bisect (if needed)
└─ Background agent: Git bisect to find breaking commit

Phase 3: Fix
└─ General-purpose agent: Implement and verify fix
```

---

## Refactoring

### Pattern: Map-Analyze-Transform

```
User Request: "Refactor callback-based code to async/await"

Phase 1: MAP (Find all instances)
└─ Explore agent: Find all callback patterns in codebase

Phase 2: FAN-OUT (Analyze impact)
├─ Agent A: Analyze module A dependencies
├─ Agent B: Analyze module B dependencies
└─ Agent C: Analyze module C dependencies

Phase 3: PIPELINE (Safe transformation)
├─ Plan agent: Design migration order (leaf nodes first)
└─ General-purpose agent: Transform files in dependency order
```

### Pattern: Strangler Fig

For large refactors, wrap old with new:

```
Phase 1: Create parallel implementation
├─ Agent A: Build new abstraction layer
└─ Agent B: Implement new pattern alongside old

Phase 2: Gradual migration
└─ General-purpose agents: Migrate consumers one by one

Phase 3: Cleanup
└─ General-purpose agent: Remove old implementation
```

---

## Migration

### Pattern: Schema-Data-Code

```
User Request: "Migrate from MongoDB to PostgreSQL"

Phase 1: FAN-OUT (Analysis)
├─ Explore agent: Document all MongoDB schemas
├─ Explore agent: Find all database queries
└─ Explore agent: Identify data transformation needs

Phase 2: PIPELINE (Schema)
└─ General-purpose agent: Create PostgreSQL schemas, migrations

Phase 3: FAN-OUT (Code updates)
├─ Agent A: Update user-related queries
├─ Agent B: Update product-related queries
└─ Agent C: Update order-related queries

Phase 4: PIPELINE (Data migration)
└─ General-purpose agent: Write and run data migration scripts
```

### Pattern: Version Upgrade

```
User Request: "Upgrade React from v17 to v18"

Phase 1: EXPLORE
└─ Explore agent: Find breaking changes, deprecated APIs used

Phase 2: MAP-REDUCE
├─ Agent A: Update component files batch 1
├─ Agent B: Update component files batch 2
└─ Agent C: Update component files batch 3
→ Aggregate: Collect all breaking changes found

Phase 3: PIPELINE
├─ General-purpose agent: Fix breaking changes
└─ Background agent: Run full test suite
```

---

## Greenfield Development

### Pattern: Scaffold-Parallel-Integrate

```
User Request: "Build a REST API for task management"

Phase 1: PIPELINE (Foundation)
├─ Plan agent: Design API architecture, endpoints, data models
└─ General-purpose agent: Scaffold project, setup tooling

Phase 2: FAN-OUT (Core features)
├─ Agent A: User management (model, routes, auth)
├─ Agent B: Task CRUD operations
├─ Agent C: Project/workspace management
└─ Agent D: Shared middleware, utilities

Phase 3: FAN-OUT (Cross-cutting)
├─ Agent A: Error handling, validation
├─ Agent B: Logging, monitoring setup
└─ Agent C: API documentation

Phase 4: PIPELINE (Polish)
└─ General-purpose agent: Integration tests, final wiring
```

---

## Task Management Integration

For any software development task, create explicit tasks:

```bash
# Decompose the work
npx cc-mirror tasks create --subject "Analyze requirements" --description "Understand codebase patterns, existing code..."
npx cc-mirror tasks create --subject "Design approach" --description "Plan implementation strategy..."
npx cc-mirror tasks create --subject "Implement core functionality" --description "Build the main feature..."
npx cc-mirror tasks create --subject "Add error handling" --description "Handle edge cases, validation..."
npx cc-mirror tasks create --subject "Write tests" --description "Unit and integration tests..."

# Set dependencies
npx cc-mirror tasks update 2 --add-blocked-by 1
npx cc-mirror tasks update 3 --add-blocked-by 2
npx cc-mirror tasks update 4 --add-blocked-by 3
npx cc-mirror tasks update 5 --add-blocked-by 3
```

```python
# Track in session
TodoWrite([
    {"content": "Analyze requirements", "status": "in_progress", "activeForm": "Analyzing requirements"},
    {"content": "Design approach", "status": "pending", "activeForm": "Designing approach"},
    {"content": "Implement core functionality", "status": "pending", "activeForm": "Implementing core"},
    {"content": "Add error handling", "status": "pending", "activeForm": "Adding error handling"},
    {"content": "Write tests", "status": "pending", "activeForm": "Writing tests"}
])

# Spawn agents for unblocked tasks (haiku for analysis/exploration)
Task(subagent_type="Explore", prompt="Task 1: Analyze requirements...",
     model="haiku", run_in_background=True)
```

Mark tasks resolved immediately upon completion:

```bash
npx cc-mirror tasks update 1 --status resolved
```

---

```
─── ◈ Software Development ─────────────
```
