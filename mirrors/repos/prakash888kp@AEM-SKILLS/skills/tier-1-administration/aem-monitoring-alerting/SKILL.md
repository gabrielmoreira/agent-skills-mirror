# AEM Monitoring & Alerting

## Purpose
Implement comprehensive monitoring, health checks, alerting, and observability for AEM instances covering system metrics, application performance, content operations, and user experience indicators.

## When to Use (Triggers)
- User mentions "monitoring," "health check," "alerting," or "observability"
- References to Sling Health Checks, JMX MBeans, or AEM operations dashboard
- Questions about system metrics, performance baselines, or SLA compliance
- Requests involving log aggregation, APM integration, or incident response
- Discussion of AEM Cloud Service monitoring or Adobe Cloud Manager

## Core Capabilities
- Configure Sling Health Checks for custom application and content validation
- Set up JMX MBean monitoring for repository, replication, and workflow metrics
- Integrate with external APM tools (New Relic, Datadog, Dynatrace, Splunk)
- Design alerting rules with severity levels and escalation paths
- Implement custom dashboards for content operations visibility

## Domain Knowledge Required
### Technical Foundation
- Sling Health Check framework (tags, composite checks, cron-scheduled execution)
- JMX MBean architecture and available AEM/Oak MBeans
- Log4j/SLF4J logging configuration and log levels in AEM
- OpenTelemetry / distributed tracing concepts

### AEM-Specific Context
- AEM Operations Dashboard and Health Reports console
- Cloud Manager monitoring and alerting (Cloud Service)
- Replication queue depth and agent status monitoring
- Oak repository statistics (session count, observation queue, index lag)
- Dispatcher health and cache hit ratio metrics

## Implementation Approach
### Step 1: Monitoring Strategy Definition
Define what to monitor based on SLAs and business requirements.
- Identify critical user journeys and their SLIs (Service Level Indicators)
- Define SLOs (Service Level Objectives) for response time, availability, error rate
- Map infrastructure dependencies (author, publish, dispatcher, CDN)
- Determine alerting thresholds and severity levels

### Step 2: Health Check Implementation
Build custom health checks for application-specific validation.
- Create Sling Health Check OSGi components with `@HealthCheck` annotation
- Define check tags for grouping (content, performance, security, integration)
- Implement composite health checks for aggregate status
- Configure MBean-based health checks for system metrics

### Step 3: Metric Collection
Set up metric gathering from all AEM layers.
- Configure JMX metric exporters for repository/workflow/replication stats
- Enable request logging and response time tracking
- Set up Sling metrics (timer, counter, histogram) for custom code
- Configure log-based metric extraction for error rates

### Step 4: Alerting Configuration
Build alerting rules with proper thresholds and routing.
- Define critical alerts (immediate page: system down, replication failure)
- Define warning alerts (Slack notification: queue depth high, slow queries)
- Configure alert suppression during maintenance windows
- Set up escalation paths for unacknowledged alerts

### Step 5: Dashboard & Visualization
Create operational dashboards for different audiences.
- Build technical dashboards (JVM, Oak, query performance, replication)
- Create content operations dashboards (publish rates, workflow completion)
- Design executive dashboards (availability, SLA compliance, content velocity)
- Implement anomaly detection for traffic and error patterns

## Quality Checklist
- [ ] Health checks cover all critical system components
- [ ] Alerting thresholds validated against actual baselines
- [ ] No alert fatigue — every alert requires action
- [ ] Dashboard loading time under 5 seconds
- [ ] Monitoring covers author, publish, and dispatcher tiers
- [ ] Log aggregation captures all instances with proper correlation
- [ ] Incident runbooks linked to each alert type
- [ ] Monitoring itself is monitored (meta-monitoring)

## Related Skills
- aem-performance-tuning-profiling (performance baselines)
- aem-debugging-log-analysis (log-based troubleshooting)
- aem-backup-disaster-recovery (recovery monitoring)

## Example Use Cases
1. **Enterprise SLA Dashboard:** Build monitoring covering 99.9% availability SLA with automated incident creation, replication queue alerts, and monthly SLA compliance reporting.
2. **Content Publishing Pipeline Monitor:** Track end-to-end content publishing from author save to CDN availability, alerting on replication delays exceeding 30 seconds and dispatcher cache invalidation failures.
3. **Cloud Service Health Automation:** Implement Cloud Manager-compatible health checks that validate content integrity, integration endpoint availability, and custom application logic after each deployment.

## Notes
- AEM Cloud Service has built-in monitoring via Cloud Manager — extend rather than replace
- Sling Health Checks should be lightweight — avoid expensive queries in health check execution
- JMX MBeans are not available on publish in Cloud Service — use alternative metric collection
- Alert on symptoms (user impact) rather than causes (CPU usage) when possible
