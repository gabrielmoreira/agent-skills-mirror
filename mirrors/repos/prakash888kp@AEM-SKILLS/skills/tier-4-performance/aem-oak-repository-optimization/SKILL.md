# AEM Oak Repository Optimization

## Purpose
Optimize Apache Oak/JCR repository performance including index management, compaction, storage configuration, and query-level tuning for AEM's content repository layer.

## When to Use (Triggers)
- User mentions "Oak," "repository," "index," "compaction," or "JCR performance"
- References to Lucene indexes, property indexes, or traversal queries
- Questions about repository growth, segment store, or document store
- Requests involving Oak query optimization, explain plans, or index definitions
- Discussion of async indexing, reindexing, or index corruption

## Core Capabilities
- Design and implement custom Oak Lucene and property indexes
- Configure online compaction and revision garbage collection
- Optimize content node structure for repository performance
- Diagnose and fix traversal queries using explain plans
- Manage Oak index lifecycle (creation, updates, reindexing)

## Domain Knowledge Required
### Technical Foundation
- Apache Jackrabbit Oak architecture (NodeStore, BlobStore, index subsystem)
- Lucene index internals (analyzers, field types, aggregation, suggestions)
- B-tree property indexes vs. Lucene full-text indexes
- Storage backends: TarMK (segment), DocumentMK (MongoDB), RDB

### AEM-Specific Context
- OOTB Oak indexes in AEM (`damAssetLucene`, `cqPageLucene`, `ntBaseLucene`)
- AEM index definition structure under `/oak:index/`
- Async indexing lanes (async, fulltext-async, elastic-async)
- AEM Cloud Service index management via Cloud Manager
- Oak query engine query plan selection and cost estimation

## Implementation Approach
### Step 1: Query Analysis
Identify queries needing optimization.
- Enable Oak query logging (`org.apache.jackrabbit.oak.query` at DEBUG)
- Review `error.log` for traversal warnings (queries traversing >100K nodes)
- Use Query Performance tool in AEM Operations console
- Generate explain plans for slow queries

### Step 2: Index Design
Create indexes targeting identified query patterns.
- Define property index for equality/range queries on specific properties
- Create Lucene index for full-text search or complex multi-property queries
- Configure index rules with property definitions (ordered, analyzed, nodeScopeIndex)
- Set appropriate includedPaths/excludedPaths to limit index scope

### Step 3: Index Deployment
Deploy indexes safely with minimal disruption.
- Create index definition under `/oak:index/` with `reindex=true`
- For Cloud Service: deploy via CI/CD pipeline with index migration
- Monitor async indexing progress via JMX MBeans
- Validate index is used via explain plan after deployment

### Step 4: Repository Maintenance
Configure ongoing repository health operations.
- Schedule online compaction (revision GC) during low-traffic windows
- Configure checkpoint management and cleanup
- Monitor repository size growth and blob store usage
- Implement data store garbage collection for unused binaries

### Step 5: Content Structure Optimization
Optimize node structure for repository performance.
- Flatten deep hierarchies where possible (avoid >8 levels)
- Use Oak-ordered indexes for sorted queries instead of in-memory sorting
- Implement bucket patterns for nodes with >1000 children
- Move large binary properties to separate nodes/data store

## Quality Checklist
- [ ] No traversal queries in production (all queries use indexes)
- [ ] Custom indexes have appropriate scope (not over-broad)
- [ ] Online compaction running successfully on schedule
- [ ] Repository growth rate within expected bounds
- [ ] Async indexing lag under 60 seconds during normal operation
- [ ] Index definitions version-controlled and deployable
- [ ] No duplicate or redundant indexes consuming resources
- [ ] Query explain plans documented for critical queries

## Related Skills
- aem-query-optimization (query writing best practices)
- aem-performance-tuning-profiling (overall performance)
- aem-monitoring-alerting (repository health monitoring)

## Example Use Cases
1. **DAM Search Performance:** Create custom Lucene index for asset search covering metadata fields (dc:title, dam:scene, product SKU) with analyzers for partial matching and phonetic search.
2. **Content Migration Optimization:** Pre-create indexes for content migration queries, configure bulk indexing mode, and manage post-migration reindexing with minimal impact on running system.
3. **Repository Size Management:** Implement comprehensive repository maintenance including segment compaction scheduling, data store GC for orphaned binaries, and version purge reducing repository from 500GB to 200GB.

## Notes
- Never reindex `lucene` or `damAssetLucene` on production without scheduling downtime — it can take hours
- AEM Cloud Service manages Oak indexes differently — deploy index definitions via CI/CD, not manual reindex
- Property indexes are faster for simple equality queries; Lucene indexes are needed for full-text or complex conditions
- Oak traversal limit is 100,000 nodes by default — queries exceeding this will fail in Cloud Service
