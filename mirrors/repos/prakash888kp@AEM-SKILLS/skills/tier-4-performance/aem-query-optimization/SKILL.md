# AEM Query Optimization

## Purpose
Write, analyze, and optimize JCR queries (SQL2, XPath, QueryBuilder) for maximum performance including proper index utilization, result set management, and query pattern best practices.

## When to Use (Triggers)
- User mentions "query," "QueryBuilder," "SQL2," "XPath," or "search"
- References to slow queries, traversal warnings, or query explain plans
- Questions about search predicates, result pagination, or faceted search
- Requests involving content queries for components, servlets, or workflows
- Discussion of query performance, index usage, or query limits

## Core Capabilities
- Write optimized queries using QueryBuilder API, JCR-SQL2, and XPath
- Analyze query explain plans and optimize for index utilization
- Implement efficient pagination, sorting, and result limiting
- Design search experiences with facets, suggestions, and fulltext
- Convert between query languages and select the most efficient approach

## Domain Knowledge Required
### Technical Foundation
- JCR query languages: SQL2, XPath, and their capabilities
- Query optimizer behavior: cost estimation, index selection, traversal
- Pagination patterns: offset vs. keyset, cursor-based pagination
- Full-text search concepts: analyzers, stemming, boost, relevance

### AEM-Specific Context
- QueryBuilder API predicates and parameter syntax
- QueryBuilder PredicateEvaluator extension mechanism
- AEM Query Debugger tool (query explain, timing)
- Oak query engine traversal limits and configuration
- Index cost estimation and query plan selection
- Common OOTB indexes and their covered query patterns

## Implementation Approach
### Step 1: Query Requirements
Define what data needs to be retrieved and how.
- Identify the content type and properties to query
- Determine filtering conditions (path, type, property values, date ranges)
- Define sorting requirements and sort index availability
- Establish result size expectations and pagination needs

### Step 2: Query Writing
Craft the query using the appropriate language.
- Use QueryBuilder for dynamic, programmatic query construction
- Use JCR-SQL2 for complex joins or subqueries
- Apply path restrictions to narrow query scope
- Include nodetype restrictions for Oak index optimization
- Limit results explicitly (p.limit in QueryBuilder)

### Step 3: Explain Plan Analysis
Validate query uses indexes effectively.
- Run query through AEM Query Debugger (Tools → Query Performance)
- Check explain plan for "traverse" vs. "index" execution
- Verify estimated cost and actual node traversal count
- Identify missing indexes for covered properties

### Step 4: Performance Optimization
Apply optimization techniques to problematic queries.
- Add path restrictions to reduce search scope
- Ensure property used in WHERE clause exists in an index
- Use native full-text constraints for text search (not LIKE '%x%')
- Implement keyset pagination instead of offset for large result sets
- Cache query results when data freshness allows

### Step 5: Production Safeguards
Prevent queries from impacting system performance.
- Set query traversal limits appropriate for the use case
- Implement query timeout handling in application code
- Add fallback behavior for query limit exceeded scenarios
- Monitor production query performance and traversal counts

## Quality Checklist
- [ ] Query uses Oak index (explain plan shows no traversal)
- [ ] Path restriction applied and as narrow as possible
- [ ] Results limited — no unbounded queries in production
- [ ] Pagination implemented efficiently (keyset for large sets)
- [ ] Query tested with production-scale data volume
- [ ] No LIKE '%value%' patterns (use full-text instead)
- [ ] Sort clause covered by index ordering
- [ ] Fallback behavior handles query timeout/limit exceeded

## Related Skills
- aem-oak-repository-optimization (index management)
- aem-performance-tuning-profiling (query in performance context)
- aem-debugging-log-analysis (query debugging)

## Example Use Cases
1. **Content Listing Component:** Implement a dynamic content listing with QueryBuilder using path, tag, and date range filters with pagination, sorting by publish date, and result count display.
2. **Asset Search Service:** Build a DAM search service supporting metadata search, file type filtering, size ranges, and faceted results using custom Lucene index with analyzed fields for partial matching.
3. **Workflow Query Optimization:** Fix a content approval workflow querying all pending items across the repository by adding path/type restrictions, proper indexing, and result limiting to prevent traversal on 1M+ node trees.

## Notes
- QueryBuilder adds overhead compared to raw JCR-SQL2 — for performance-critical code, use SQL2 directly
- Offset-based pagination degrades linearly — keyset pagination maintains constant performance
- AEM Cloud Service enforces traversal limits strictly — queries must use indexes or they will fail
- LIKE predicates with leading wildcards ('LIKE %term%') cannot use indexes — use full-text contains()
