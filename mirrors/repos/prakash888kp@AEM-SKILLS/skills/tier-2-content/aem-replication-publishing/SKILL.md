# AEM Replication & Publishing

## Purpose
Configure and manage content replication between AEM instances including publish agents, reverse replication, content distribution, and publish queue management.

## When to Use (Triggers)
- User mentions "replication," "publishing," "activation," or "content distribution"
- References to replication agents, publish queues, or tree activation
- Questions about content sync, reverse replication, or distribution packages
- Requests involving publish failures, queue management, or agent configuration
- Discussion of Sling Content Distribution (Cloud Service) or CRX DE replication

## Core Capabilities
- Configure forward and reverse replication agents
- Implement Sling Content Distribution for AEM Cloud Service
- Design content distribution topologies (single publish, publish farm)
- Troubleshoot replication queue blockages and serialization errors
- Set up content invalidation and flush agents for dispatcher

## Domain Knowledge Required
### Technical Foundation
- Replication agent architecture (transport, serialization, triggers)
- Sling Content Distribution (Golden Publish, queue-based distribution)
- HTTP/HTTPS transport layer and authentication for replication
- JCR observation and event-based replication triggers

### AEM-Specific Context
- Agent types: default, reverse, static, flush, custom
- Replication queue management (block, retry, force retry, clear)
- Tree activation vs. individual page activation
- On-modification vs. on-receive triggers
- Content distribution in AEM Cloud Service (no traditional replication)

## Implementation Approach
### Step 1: Topology Design
Plan the replication architecture based on requirements.
- Map author → publish instances and their relationships
- Determine if Sling Content Distribution applies (Cloud Service)
- Plan dispatcher flush agent configuration
- Design reverse replication for UGC or form submissions

### Step 2: Agent Configuration
Set up replication agents for each connection.
- Configure transport URI and authentication
- Set serialization type (default, dispatcher flush, static)
- Define trigger settings (on-modification, on-receive, scheduled)
- Configure retry and batch settings for performance

### Step 3: Queue Management
Implement monitoring and handling for distribution queues.
- Set up queue monitoring with size and age alerts
- Configure dead-letter queues for persistent failures
- Implement automatic retry with exponential backoff
- Plan manual intervention procedures for blocked queues

### Step 4: Content Distribution Patterns
Define how different content types are distributed.
- Configure tree activation for bulk publishing
- Set up scheduled activation for time-sensitive content
- Implement deep vs. shallow activation strategies
- Handle reference resolution for linked assets and pages

### Step 5: Validation & Monitoring
Ensure replication reliability and performance.
- Test replication agent connectivity and authentication
- Validate content integrity post-replication
- Monitor replication latency (author-to-publish delay)
- Set up alerting for queue depth and failure rates

## Quality Checklist
- [ ] All publish instances receive content within SLA time
- [ ] Replication queues drain under normal load without blocking
- [ ] Failed replication creates actionable alerts
- [ ] Dispatcher flush agents invalidate correct cache paths
- [ ] Reverse replication captures UGC without data loss
- [ ] Bulk activation handles 1000+ pages without timeout
- [ ] Agent credentials stored securely (not in plain text)
- [ ] Content integrity verified between author and publish

## Related Skills
- aem-dispatcher-configuration (cache invalidation via flush agents)
- aem-caching-strategy (cache coherency with replication)
- aem-monitoring-alerting (replication queue monitoring)

## Example Use Cases
1. **Multi-Region Publish Farm:** Configure replication to 6 publish instances across 3 geographic regions with dispatcher flush agents ensuring cache consistency and regional failover support.
2. **Scheduled Go-Live:** Implement timed activation for a product launch requiring 500+ pages and 2000+ assets to go live simultaneously at a specific date/time across all markets.
3. **User-Generated Content Pipeline:** Set up reverse replication from publish instances to author for comment moderation, form submissions, and user rating aggregation with conflict resolution.

## Notes
- AEM Cloud Service uses Sling Content Distribution — traditional replication agents don't apply
- Tree activation is resource-intensive — schedule during low-traffic periods
- Flush agents should target dispatcher, not publish instances directly
- Replication of large binaries (video, PDFs) may require dedicated agents with higher timeouts
