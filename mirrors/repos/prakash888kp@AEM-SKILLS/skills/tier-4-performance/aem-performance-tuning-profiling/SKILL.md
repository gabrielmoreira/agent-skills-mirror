# AEM Performance Tuning & Profiling

## Purpose
Identify, diagnose, and resolve performance bottlenecks in AEM using profiling tools, thread analysis, heap inspection, and systematic optimization of request processing pipelines.

## When to Use (Triggers)
- User mentions "performance," "slow," "profiling," "thread dump," or "optimization"
- References to response time issues, high CPU, memory leaks, or GC pressure
- Questions about JVM tuning, thread analysis, or heap dump investigation
- Requests involving load testing, performance baselines, or capacity planning
- Discussion of AEM performance best practices or optimization strategies

## Core Capabilities
- Capture and analyze thread dumps for deadlocks and contention
- Profile heap usage and identify memory leaks via MAT/VisualVM
- Tune JVM parameters (heap, GC algorithm, thread pools) for AEM workloads
- Optimize request processing pipeline (Sling resolution, filter chain, rendering)
- Establish performance baselines and regression detection

## Domain Knowledge Required
### Technical Foundation
- JVM internals (heap regions, GC algorithms: G1GC, ZGC, Shenandoah)
- Thread dump analysis (WAITING, BLOCKED, RUNNABLE states, lock contention)
- Memory profiling (dominator trees, retained heap, class histogram)
- HTTP request lifecycle and server thread pool management

### AEM-Specific Context
- Sling request processing pipeline (resource resolution, servlet selection, filter chain)
- AEM request logging and timing (request.log analysis, TIMER patterns)
- Oak session management and its performance implications
- Bundle class loading and its impact on startup and runtime performance
- Tar segment store vs. document store performance characteristics

## Implementation Approach
### Step 1: Problem Identification
Define the performance issue precisely.
- Identify affected user journeys and their current response times
- Determine if issue is latency, throughput, or resource exhaustion
- Establish baseline metrics for comparison
- Categorize: author-side, publish-side, or dispatcher-side issue

### Step 2: Data Collection
Gather diagnostic data for analysis.
- Capture thread dumps (3+ dumps, 10 seconds apart) during issue occurrence
- Collect request.log entries for slow requests (>5s threshold)
- Generate heap dump if memory-related (jmap or jcmd)
- Gather GC logs for garbage collection analysis
- Collect Oak query statistics for repository performance

### Step 3: Analysis
Interpret collected data to identify root cause.
- Analyze thread dumps for blocked threads and lock contention
- Use MAT (Memory Analyzer Tool) for heap dump investigation
- Review request timing breakdown (resource resolution, model execution, HTL render)
- Identify N+1 query patterns or excessive session operations
- Check for resource leaks (unclosed sessions, connections)

### Step 4: Optimization
Implement targeted fixes based on analysis.
- Tune JVM parameters (heap size, GC settings, thread pool sizes)
- Optimize identified code paths (caching, lazy loading, async processing)
- Restructure queries or content for faster resolution
- Implement connection pooling or resource pooling where applicable
- Add caching layers for expensive operations

### Step 5: Validation
Confirm optimization effectiveness.
- Run load tests comparing before/after metrics
- Verify no regressions in other areas
- Monitor production metrics post-deployment
- Document optimization decisions and their measured impact

## Quality Checklist
- [ ] Performance issue quantified with specific metrics (response time, throughput)
- [ ] Root cause identified with evidence (thread dumps, profiles, logs)
- [ ] Fix addresses root cause, not just symptoms
- [ ] No memory leaks introduced (validated with heap analysis)
- [ ] Load test confirms improvement under realistic traffic
- [ ] JVM settings documented and appropriate for instance size
- [ ] Performance regression detection in place for future changes
- [ ] Documentation updated with optimization rationale

## Related Skills
- aem-query-optimization (JCR/Oak query performance)
- aem-caching-strategy (caching as optimization technique)
- aem-monitoring-alerting (performance metric tracking)

## Example Use Cases
1. **Author UI Slowness:** Diagnose Sites console taking 30+ seconds to load for a site with 10,000+ pages by analyzing thread dumps, identifying Oak query traversals, and implementing index optimization.
2. **Publish Throughput Degradation:** Investigate publish instance degradation under load using thread dump analysis to find session contention, heap analysis for cache inefficiency, and request log timing breakdown.
3. **Memory Leak Investigation:** Track down a gradual memory increase over 72 hours using periodic heap dumps, MAT dominator tree analysis, and class histogram comparison to identify the leaking object graph.

## Notes
- Always collect multiple thread dumps — a single dump is a snapshot, not a trend
- AEM Cloud Service provides predefined JVM settings — focus optimization on application code
- G1GC is the recommended garbage collector for AEM 6.5+ with heap > 6GB
- Request.log `TIMER` entries provide built-in performance profiling without additional tooling
