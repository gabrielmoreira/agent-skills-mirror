# AEM Integration Framework & Adobe I/O

## Purpose
Implement integrations between AEM and external systems using Adobe I/O Runtime, Adobe Developer Console, cloud connectors, and custom integration patterns.

## When to Use (Triggers)
- User mentions "integration," "Adobe I/O," "Adobe Developer Console," or "cloud connector"
- References to external APIs, third-party services, or system integration
- Questions about event-driven architecture, webhooks, or Adobe I/O Events
- Requests involving Adobe Experience Platform, Analytics, Target, or Campaign integration
- Discussion of custom connectors, data sync, or middleware patterns

## Core Capabilities
- Configure Adobe I/O integrations with service credentials and JWT/OAuth
- Implement Adobe I/O Runtime actions for serverless integration logic
- Set up Adobe I/O Events for event-driven AEM integrations
- Design integration patterns for CRM, ERP, PIM, and marketing platforms
- Build custom Cloud Service configurations for third-party APIs

## Domain Knowledge Required
### Technical Foundation
- OAuth 2.0 and JWT authentication flows
- RESTful API integration patterns (retry, circuit breaker, timeout)
- Event-driven architecture (pub/sub, webhooks, event sourcing)
- Serverless function design (stateless, idempotent, timeout-aware)

### AEM-Specific Context
- Cloud Services configuration framework (`/conf/<project>/settings/cloudconfigs/`)
- Adobe IMS integration and service credentials
- Adobe I/O Events registration and event handling
- Sling Content Distribution events for AEM-to-external triggers
- Integration with Adobe Experience Platform (AEP) and Real-Time CDP

## Implementation Approach
### Step 1: Integration Architecture
Design the integration topology and data flow.
- Map source/target systems and data direction (push, pull, bidirectional)
- Define integration pattern (sync request, async event, batch ETL)
- Plan error handling and retry strategy
- Determine authentication and authorization approach

### Step 2: Adobe I/O Configuration
Set up project and credentials in Adobe Developer Console.
- Create Adobe I/O project with appropriate APIs and services
- Configure service credentials (OAuth Server-to-Server or JWT deprecated)
- Set up environment-specific credential management
- Register webhooks and event subscriptions

### Step 3: Cloud Service Configuration
Build the AEM-side configuration for the integration.
- Create Cloud Service configuration under `/conf/<project>/settings/`
- Implement configuration dialog for credentials and endpoints
- Set up environment-specific OSGI configurations for endpoints
- Build health check for integration availability validation

### Step 4: Integration Logic
Implement the data exchange and transformation.
- Build I/O Runtime actions for complex transformation logic
- Implement Sling servlets for inbound API endpoints
- Create workflow process steps for integration-triggered actions
- Handle data mapping and format transformation

### Step 5: Monitoring & Error Handling
Ensure integration reliability and observability.
- Implement circuit breaker for external service failures
- Set up dead letter queues for failed integrations
- Configure alerting on integration failures and latency
- Build retry logic with exponential backoff

## Quality Checklist
- [ ] Credentials stored securely (not in code, using Cloud Service config)
- [ ] Integration handles external service downtime gracefully
- [ ] Retry logic prevents data loss without creating duplicates
- [ ] All API calls timeout within acceptable limits (< 30s)
- [ ] Integration health check available for monitoring
- [ ] Data validation at integration boundaries prevents corrupt data
- [ ] Audit logging captures all integration transactions
- [ ] Performance impact on AEM measured and acceptable

## Related Skills
- aem-webhook-event-driven-architecture (event patterns)
- aem-custom-osgi-services (service implementation)
- aem-monitoring-alerting (integration monitoring)

## Example Use Cases
1. **PIM Integration:** Sync 50,000 product records from a Product Information Management system into AEM Content Fragments nightly, with delta detection, conflict resolution, and automated publishing of updated products.
2. **Adobe Target Personalization:** Integrate AEM Experience Fragments with Adobe Target for A/B testing and automated personalization, including offer creation API, activity sync, and analytics event correlation.
3. **CRM-Driven Personalization:** Connect Salesforce CRM data with AEM personalization engine via Adobe I/O Events, triggering content updates when customer segments change and delivering personalized landing pages.

## Notes
- JWT service credentials are deprecated — migrate to OAuth Server-to-Server credentials
- Adobe I/O Runtime has execution time limits (60s default) — design for short-lived functions
- Cloud Service configurations are context-aware — bind to content paths for multi-site support
- Always implement idempotent integration handlers — events/webhooks may be delivered multiple times
