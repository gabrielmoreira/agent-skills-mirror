# Power BI Performance Assessment Report

## Report Information

| Field | Value |
|-------|-------|
| **Assessment Date** | _YYYY-MM-DD_ |
| **Assessed By** | _Name_ |
| **Workspace** | _Workspace Name_ |
| **Capacity SKU** | _F## / P#_ |
| **Scope** | _All reports / Specific report name_ |

---

## Executive Summary

_2-3 sentence summary of key findings and the overall health of the Power BI deployment._

**Overall Health**: _Healthy / Needs Attention / Critical_

---

## Environment Overview

### Capacity

| Metric | Value | Status |
|--------|-------|--------|
| Capacity SKU | | |
| Average CU utilization (interactive) | __%  | _Healthy / Warning / Critical_ |
| Average CU utilization (background) | __% | _Healthy / Warning / Critical_ |
| Throttling events (last 7 days) | | |
| Query scale-out enabled | _Yes / No_ | |
| XMLA endpoint enabled | _Yes / No_ | |

### Semantic Models

| Model Name | Storage Mode | Size (MB) | Row Count | Refresh Duration | Last Refresh Status |
|------------|-------------|-----------|-----------|-----------------|-------------------|
| | | | | | |
| | | | | | |

### Reports

| Report Name | Visual Count | Avg Load Time | Top Slow Visual | Bottleneck Type |
|-------------|-------------|---------------|-----------------|-----------------|
| | | | | _DAX / Render / Source_ |
| | | | | |

---

## Findings

### Critical

| # | Category | Finding | Impact | Recommendation |
|---|----------|---------|--------|---------------|
| 1 | | | | |
| 2 | | | | |

### Warning

| # | Category | Finding | Impact | Recommendation |
|---|----------|---------|--------|---------------|
| 1 | | | | |
| 2 | | | | |

### Informational

| # | Category | Finding | Impact | Recommendation |
|---|----------|---------|--------|---------------|
| 1 | | | | |
| 2 | | | | |

---

## DAX Measure Analysis

### Anti-Patterns Detected

| Measure | Table | Pattern | Severity | Recommendation |
|---------|-------|---------|----------|---------------|
| | | | | |

### Complex Measures (> 20 lines or > 5 nested functions)

| Measure | Table | Lines | Nested Functions | Uses Variables |
|---------|-------|-------|-----------------|---------------|
| | | | | |

### Measures Missing Descriptions

| Measure | Table |
|---------|-------|
| | |

---

## Report Design Analysis

### Page-Level Metrics

| Page Name | Visual Count | Cross-Filter Chains | High-Cardinality Visuals | Slicer Count |
|-----------|-------------|-------------------|------------------------|-------------|
| | | | | |

### Report Design Recommendations

| Page | Issue | Recommendation | Priority |
|------|-------|---------------|----------|
| | | | |

---

## Data Source Analysis

### Query Folding Status

| Power Query Step | Folds to Source | Impact |
|-----------------|----------------|--------|
| | _Yes / No_ | |

### Source Performance

| Source | Type | Avg Query Time | Has Indexes | Recommendation |
|--------|------|---------------|-------------|---------------|
| | | | | |

---

## Action Plan

### Immediate (This Week)

| # | Action | Owner | Expected Impact |
|---|--------|-------|----------------|
| 1 | | | |
| 2 | | | |

### Short-Term (This Month)

| # | Action | Owner | Expected Impact |
|---|--------|-------|----------------|
| 1 | | | |
| 2 | | | |

### Long-Term (This Quarter)

| # | Action | Owner | Expected Impact |
|---|--------|-------|----------------|
| 1 | | | |
| 2 | | | |

---

## Appendix

### Tools Used

- Power BI Desktop Performance Analyzer
- DAX Studio (version: ___)
- Tabular Editor / Best Practice Analyzer
- Fabric Capacity Metrics App
- PowerShell scripts from pbi-performance-remediate skill

### References

- [Optimization guide for Power BI](https://learn.microsoft.com/en-us/power-bi/guidance/power-bi-optimization)
- [Troubleshoot report performance](https://learn.microsoft.com/en-us/power-bi/guidance/report-performance-troubleshoot)
- [Monitor report performance](https://learn.microsoft.com/en-us/power-bi/guidance/monitor-report-performance)
- [Evaluate and optimize Fabric capacity](https://learn.microsoft.com/en-us/fabric/enterprise/optimize-capacity)
