# Power BI Performance remediate Flowchart

## Table of Contents

- [Phase 1: Identify the Scope](#phase-1-identify-the-scope)
- [Phase 2: Capacity Health Check](#phase-2-capacity-health-check)
- [Phase 3: Report-Level Diagnosis](#phase-3-report-level-diagnosis)
- [Phase 4: Semantic Model Diagnosis](#phase-4-semantic-model-diagnosis)
- [Phase 5: Data Source Diagnosis](#phase-5-data-source-diagnosis)
- [Phase 6: Environment Diagnosis](#phase-6-environment-diagnosis)
- [Decision Matrix](#decision-matrix)

---

## Phase 1: Identify the Scope

**Question**: Is the slowness affecting all reports or specific ones?

| Answer | Next Step |
|--------|-----------|
| All reports on this capacity | Go to Phase 2 (Capacity Health) |
| Specific report(s) only | Go to Phase 3 (Report-Level) |
| All reports at certain times | Go to Phase 2 (check time-based patterns) |
| Reports slow for specific users/regions | Go to Phase 6 (Environment) |

**Question**: When did the performance degrade?

| Answer | Investigation Path |
|--------|-------------------|
| Gradually over time | Data growth; check row counts, model size, refresh duration trend |
| Suddenly after a change | Identify recent deployments, data source changes, capacity changes |
| Always been slow | Likely design issue; full audit recommended |
| Intermittent / unpredictable | Capacity contention or external dependency |

---

## Phase 2: Capacity Health Check

### Step 2.1: Open Fabric Capacity Metrics App

Navigate to the Fabric Capacity Metrics app and select your capacity.

### Step 2.2: Check Utilization

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| CU utilization (interactive) | < 50% | 50-80% | > 80% |
| CU utilization (background) | < 70% | 70-90% | > 90% |
| Throttling events | 0 | Occasional | Frequent |
| Queue depth | 0-2 | 3-10 | > 10 |

### Step 2.3: Identify Top Consumers

Sort by CU seconds to find the most expensive items. Common culprits:

- Large semantic model refreshes running during peak hours
- Paginated report bursting (many reports generated simultaneously)
- Inefficient DAX queries from heavily-used dashboards
- Dataflow Gen2 or notebook jobs competing for capacity

### Step 2.4: Resolution Actions

| Finding | Action |
|---------|--------|
| Sustained high utilization | Scale up capacity SKU or enable Autoscale |
| Spike during refresh window | Stagger refresh schedules; enable incremental refresh |
| Single item dominates | Optimize that specific item (see Phase 3 or 4) |
| Background smoothing insufficient | Consider Autoscale Billing for Spark workloads |

---

## Phase 3: Report-Level Diagnosis

### Step 3.1: Run Performance Analyzer

In Power BI Desktop:
1. View > Performance Analyzer > Start recording
2. Refresh visuals (or interact with the slow element)
3. Stop recording and expand results

### Step 3.2: Classify Bottleneck per Visual

| Duration Category | Meaning | Action |
|-------------------|---------|--------|
| DAX query > 500ms | Measure or filter inefficiency | Go to Phase 4 |
| Visual display > 500ms | Too many data points or complex rendering | Simplify visual |
| Other > 500ms | Data retrieval from source | Go to Phase 5 |

### Step 3.3: Report Design Checks

- **Visual count per page**: More than 8-10 interactive visuals causes cascading query storms
- **Cross-highlight chains**: Visuals that cross-filter each other multiply query count
- **High-cardinality tables/matrices**: Tables rendering 1000+ rows are expensive
- **Complex conditional formatting**: Row-level conditional formatting on large tables is slow
- **Too many slicers**: Each slicer adds filter context to every visual query

### Step 3.4: Report Design Fixes

| Problem | Fix |
|---------|-----|
| Too many visuals | Split into multiple pages with drill-through navigation |
| Large result set visuals | Add Top N filters, use aggregations |
| Slicer overload | Use filter pane instead, or group into fewer slicers |
| Complex page | Use bookmarks to show/hide visual groups |

---

## Phase 4: Semantic Model Diagnosis

### Step 4.1: Run Best Practice Analyzer

Using Tabular Editor or a Fabric notebook, run the Best Practice Analyzer rules. Prioritize:

1. **Columns with high cardinality** (> 1M distinct values in Import mode)
2. **Unused columns** (columns not referenced by any measure, relationship, or visual)
3. **Calculated columns** that could be measures or pushed to the source
4. **Incorrect data types** (dates stored as text, unnecessary high-precision decimals)
5. **Missing descriptions** on tables, columns, and measures

### Step 4.2: DAX Measure Profiling

Open DAX Studio and connect to the model:
1. Enable Server Timings (under Advanced)
2. Run the slow measure's query (copy from Performance Analyzer)
3. Analyze the breakdown:
   - FE (Formula Engine): In-memory calculation
   - SE (Storage Engine): Data scan from VertiPaq or DirectQuery
   - SE Queries: Number of storage engine requests

**Healthy targets:**
- Total query < 500ms
- SE queries < 20
- FE ratio < 50% of total

### Step 4.3: Storage Mode Evaluation

| Mode | Best For | Watch Out For |
|------|----------|---------------|
| Import | Interactive dashboards, complex DAX | Model size limits, refresh latency |
| DirectQuery | Real-time data, very large datasets | Query latency, source performance dependency |
| Composite | Best of both; aggregations + detail | Complexity, relationship limitations |
| Dual | Tables used in both Import and DQ contexts | Memory consumption |

### Step 4.4: Fabric-Specific Optimizations

- **VOrder**: Enable for read-heavy PBI workloads (`readHeavyForPBI` resource profile)
- **Query scale-out**: Enable for high-concurrency semantic models (F64+)
- **XMLA endpoint**: Use for advanced tooling (DAX Studio, Tabular Editor)
- **Large model format**: Enable for models > 1GB

---

## Phase 5: Data Source Diagnosis

### Step 5.1: Query Folding Check

In Power Query Editor:
1. Right-click on the last applied step
2. If "View Native Query" is available and shows valid SQL, folding is working
3. If grayed out, folding broke at that step

### Step 5.2: Common Folding Breakers

- Custom columns with M functions
- Sorting before filtering
- Merging queries from different sources
- Complex type transformations

### Step 5.3: Source-Side Optimization

| Source Type | Optimization |
|-------------|-------------|
| SQL Server / Synapse | Add indexes on filter/join columns; create indexed views |
| Lakehouse SQL endpoint | Ensure tables are Delta format; enable VOrder |
| Dataverse | Limit columns selected; use native query when possible |
| SharePoint / Excel | Move to Lakehouse or SQL for better performance |

---

## Phase 6: Environment Diagnosis

### Step 6.1: Network and Gateway

| Symptom | Check |
|---------|-------|
| Slow from specific regions | Network latency to Fabric region |
| Slow in Service, fast in Desktop | On-premises gateway performance |
| Intermittent timeouts | Gateway logs for errors; network stability |

### Step 6.2: Gateway Optimization

- Update to latest gateway version
- Run gateway on dedicated hardware (not shared with other workloads)
- Enable gateway clustering for high availability
- Monitor gateway performance counters

### Step 6.3: Client-Side Checks

- Browser: Test in Edge (Chromium) for best Power BI compatibility
- Device: Check available RAM and GPU acceleration
- Extensions: Disable browser extensions that might interfere

---

## Decision Matrix

Use this matrix to quickly route to the right phase based on symptoms:

| Symptom | Phase | Priority |
|---------|-------|----------|
| Everything slow on capacity | 2 | Critical |
| Single report slow | 3 | High |
| Specific visual slow | 3 → 4 | High |
| DAX query slow in profiler | 4 | High |
| Refresh takes too long | 4 → 5 | Medium |
| DirectQuery timeouts | 5 | High |
| Slow for remote users only | 6 | Medium |
| Slow after deploying changes | 3 → 4 | High |
| Slow at peak hours only | 2 | Medium |
