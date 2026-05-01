---
name: product-analytics-instrumentation
description: Design, audit, and improve product analytics instrumentation, event taxonomy, telemetry schemas, funnels, activation metrics, retention metrics, tracking plans, observability events, QA, and data quality. Use when Codex is asked about product analytics events, app/game telemetry, funnel instrumentation, analytics implementation, event naming, properties, user identity, or measurement-ready product design.
license: MIT
---

# Product Analytics Instrumentation

## Core Workflow

1. Define the product decision, user journey, and metric questions before naming events.
2. Map the journey: acquisition, onboarding, activation, core loop, conversion, retention, expansion, referral, failure, and support.
3. Design event taxonomy with consistent names, required properties, optional properties, identity rules, timestamps, source, and versioning.
4. Separate product analytics events from technical observability signals, while preserving useful joins between them.
5. Plan implementation and QA: trigger conditions, deduplication, consent, privacy, test users, environments, and validation queries.
6. Define dashboard and analysis use cases before instrumenting extra data.
7. Maintain the taxonomy: ownership, change review, deprecation, documentation, and data quality checks.

## Freshness Rule

Verify current analytics, privacy, SDK, consent, and observability documentation before giving platform-specific advice for GA4, Firebase, Amplitude, Segment, PostHog, Mixpanel, OpenTelemetry, data warehouses, or mobile/game SDKs.

## Instrumentation Principles

- Track meaningful user behavior, not every click.
- Name events consistently and in business language where possible.
- Use properties for context, not to hide separate actions.
- Avoid high-cardinality dimensions in metrics systems unless the backend supports them and the use case justifies it.
- Keep PII and sensitive data out of analytics events unless there is a clear legal basis and privacy review.
- QA analytics like product behavior: event fires once, at the right time, with the right properties, in the right environment.

## Deliverable Shape

For analytics instrumentation work, provide:

- Decision questions and product journey
- North-star, activation, funnel, retention, and guardrail metrics
- Event taxonomy or tracking plan
- Identity, privacy, and consent assumptions
- Implementation notes
- QA and data-quality checks
- Dashboard or analysis plan

## References

- Read `references/product-analytics-checklist.md` when designing or reviewing product analytics instrumentation.
