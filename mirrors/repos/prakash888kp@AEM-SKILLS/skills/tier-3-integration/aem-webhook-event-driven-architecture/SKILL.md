# AEM Webhook & Event-Driven Architecture

## Purpose
Design and implement event-driven integrations using AEM Events, Adobe I/O Events, custom webhooks, and event processing pipelines for real-time content and system reactions.

## When to Use (Triggers)
- User mentions "webhook," "events," "event-driven," "event handler," or "event listener"
- References to Adobe I/O Events, Sling events, JCR observation, or OSGi events
- Questions about real-time notifications, content change triggers, or async processing
- Requests involving pub/sub patterns, event sourcing, or reactive architectures
- Discussion of system integration through events rather than polling

## Core Capabilities
- Implement JCR observation listeners for content change detection
- Configure Adobe I/O Events for cloud-native event distribution
- Build custom webhook endpoints for inbound event reception
- Design event processing pipelines with filtering and transformation
- Implement event replay, dead-letter handling, and at-least-once delivery

## Domain Knowledge Required
### Technical Foundation
- Event-driven architecture patterns (pub/sub, event sourcing, CQRS)
- Webhook design (signature verification, retry handling, idempotency)
- Message queue concepts (ordering, partitioning, dead-letter queues)
- Async processing patterns (fire-and-forget, request-reply, saga)

### AEM-Specific Context
- Sling Event handling (EventHandler, EventListener, TopicConsumer)
- JCR Observation API (EventListener, event types, path filters)
- Adobe I/O Events for AEM (asset events, page events, custom events)
- OSGi Event Admin service for intra-bundle communication
- Sling Jobs for reliable async processing with retry

## Implementation Approach
### Step 1: Event Architecture Design
Define event flows and processing requirements.
- Identify event sources (content changes, user actions, system events)
- Design event schema (payload structure, metadata, correlation IDs)
- Plan event routing (local processing vs. external distribution)
- Define delivery guarantees (at-most-once, at-least-once, exactly-once)

### Step 2: Event Producer Implementation
Build event emission from AEM.
- Register JCR observation listeners for content paths of interest
- Configure Adobe I/O Events registrations for AEM events
- Implement custom event emission from workflow steps or servlets
- Add event metadata (timestamp, user, correlation ID, source)

### Step 3: Event Consumer Development
Implement event processing logic.
- Build Sling Event Handlers for local event processing
- Create Sling Jobs for reliable async processing with retry
- Implement webhook receivers for inbound external events
- Design idempotent handlers to safely process duplicate events

### Step 4: Webhook Endpoint Configuration
Set up webhook infrastructure for external integration.
- Create Sling servlets as webhook receivers
- Implement signature verification (HMAC, shared secret)
- Configure request validation and payload parsing
- Set up response handling (acknowledge, reject, retry-later)

### Step 5: Reliability & Monitoring
Ensure event processing reliability.
- Implement dead-letter queues for failed event processing
- Configure retry policies with exponential backoff
- Set up event processing metrics (throughput, latency, failure rate)
- Build event replay capability for recovery scenarios

## Quality Checklist
- [ ] Events processed within latency SLA (< 5s for critical, < 60s for standard)
- [ ] Dead-letter queue captures all processing failures with context
- [ ] Webhook signature verification prevents unauthorized event injection
- [ ] Idempotent handlers safely process duplicate events
- [ ] Event processing doesn't block AEM request threads
- [ ] Monitoring tracks event backlog depth and processing rate
- [ ] Circuit breaker prevents cascade failures from slow consumers
- [ ] Event schema documented and versioned

## Related Skills
- aem-integration-framework-adobe-io (Adobe I/O Events platform)
- aem-sling-servlets-event-listeners (Sling event implementation)
- aem-custom-osgi-services (service-based event processing)

## Example Use Cases
1. **Real-Time CDN Invalidation:** Emit events on page publication that trigger CDN cache purge within 5 seconds, with confirmation webhook back to AEM updating cache status metadata.
2. **Content Sync Pipeline:** Event-driven sync from AEM to external search index (Elasticsearch/Algolia) with delta updates on content publish, full re-index capability, and consistency verification.
3. **Cross-System Workflow Orchestration:** Orchestrate multi-system content approval spanning AEM, DAM, legal review system, and translation platform using event choreography with saga pattern for rollback.

## Notes
- JCR observation listeners fire on ALL matching changes including system operations — filter carefully
- Sling Jobs provide persistent, retryable processing — prefer over raw event handlers for critical operations
- Adobe I/O Events have delivery retry built-in — don't implement your own retry for outbound events
- AEM Cloud Service restricts some JCR observation capabilities — use Adobe I/O Events where possible
