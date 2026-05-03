---
type: skill
lifecycle: stable
inheritance: inheritable
name: early-filter-optimization
description: Cross-domain early-filtering paradigm for reducing cognitive and computational load in data pipelines, AI context, and human attention
tier: standard
applyTo: '**/*early*,**/*filter*,**/*optimization*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Domain Knowledge: Early Filter Optimization


**Domain**: Cross-Domain Performance Optimization
**Mastery Level**: Applied (Real-world validation)
**Created**: 2026-01-22
**Updated**: 2026-01-22
**Source**: Meditation consolidation from SQL optimization + architecture streamlining session

---

## Core Principles

### 1. Early Filtering

> **"Don't process what you don't need. Filter early, load lazy, prune aggressively."**

This principle emerged from parallel optimization work in data engineering and cognitive architecture, revealing universal applicability.

### 2. System Readiness (Added 2026-01-22 Evening)

> **"Don't race the system. Respect its readiness. When in doubt, stage and wait."**

Complements Early Filtering by addressing temporal boundaries rather than data boundaries.

| Principle | Focus | Question |
|-----------|-------|----------|
| Early Filter | Data boundaries | *What* to process? |
| System Readiness | Temporal boundaries | *When* to proceed? |

---

## Pattern: The Early Filter Paradigm

### Manifestations Across Domains

| Domain | Anti-Pattern | Optimized Pattern | Improvement |
|--------|--------------|-------------------|-------------|
| **SQL/Data** | Full table scan, filter after | CTE pre-filter, join reduced set | 99%+ reduction |
| **Spark** | Load all data, filter in memory | Predicate pushdown, partition pruning | Order of magnitude |
| **API Design** | Return all fields, paginate client-side | Field selection, server pagination | Bandwidth + latency |
| **AI Context** | Load all instruction files always | Scope with `applyTo`, load on trigger | Reduced token overhead |
| **Human Attention** | Try to hold everything in mind | Externalize, reference on demand | Cognitive capacity |

### Implementation Strategies

1. **Push Filters Down**: Move WHERE clauses into joins, use partition keys
2. **Scope Activation**: Use patterns/triggers instead of global loading
3. **Lazy Evaluation**: Don't compute until value is actually needed
4. **Reference vs. Copy**: Point to source rather than duplicating content

---

## Case Study: UDP Commercial Query (2026-01-22)

### Before

```sql
-- CTE joins against 18M row dimension table
LEFT JOIN vwDimServiceOfferingMaster so  -- 18,094,691 rows
    ON sr.ServiceOfferingMasterKey = so.ServiceOfferingMasterKey
```

### After

```sql
-- Pre-filter dimension to only relevant keys
WITH CTE_UsedServiceOfferings AS (
    SELECT DISTINCT ServiceOfferingMasterKey
    FROM vwFactSupportServiceRequest
    WHERE ClosedTimeKey >= 20240101  -- Only 2,474 unique keys used
)
-- Then join against filtered set
LEFT JOIN CTE_FilteredServiceOffering so
    ON sr.ServiceOfferingMasterKey = so.ServiceOfferingMasterKey
```

**Result**: 7,300x reduction in dimension rows scanned

---

## Case Study: Copilot Instruction Files (2026-01-22)

### Before

```yaml
# In each .instructions.md file
applyTo: "**/*"  # Loaded in EVERY conversation
```

### After

```yaml
# No applyTo - files read only when triggered
description: "..."  # Available but not auto-loaded
```

**Result**: 13 files removed from default context, loaded only via trigger keywords in main `copilot-instructions.md`

---

## Applicability Checklist

When optimizing any system, ask:

- [ ] **What is the smallest necessary input?** (Filter early)
- [ ] **What can be deferred?** (Lazy load)
- [ ] **What is duplicated unnecessarily?** (Reference instead)
- [ ] **What never gets used?** (Prune aggressively)
- [ ] **Where is the bottleneck?** (Focus optimization there)
