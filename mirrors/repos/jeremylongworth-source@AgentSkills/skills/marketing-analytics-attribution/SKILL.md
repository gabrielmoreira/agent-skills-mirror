---
name: marketing-analytics-attribution
description: Define, audit, and improve marketing analytics, GA4 events, conversion goals, attribution, dashboards, funnel metrics, CAC, LTV, campaign measurement, experiment design, UTM governance, CRM-source reporting, and data quality checks. Use when Codex is asked to measure sales/marketing performance or diagnose reporting.
license: MIT
---

# Marketing Analytics Attribution

## Core Workflow

1. Define business questions before dashboards.
2. Map the funnel and data sources: website, product, CRM, ad platforms, email, events, sales, billing, and support.
3. Define events, properties, identities, UTMs, conversion goals, lifecycle stages, and revenue joins.
4. Separate source-of-truth reporting from exploratory reporting.
5. Validate tracking with test events, debug tools, CRM reconciliation, and known conversion paths.
6. Report decisions, not vanity metrics.

## Freshness Rule

Verify current GA4, Google Ads, and ad-platform documentation before prescribing event setup, conversion import, attribution windows, consent mode, enhanced conversions, or bidding optimization. Terminology changes: GA4 refers to important analytics events as key events, while Google Ads uses conversion actions and conversion goals for optimization/reporting.

## Measurement Priorities

- Funnel: traffic, conversion, lead quality, opportunity creation, win rate, sales cycle, revenue, retention, expansion.
- Efficiency: CAC, payback, LTV/CAC, CPA, CPL, cost per opportunity, ROAS, margin-aware return.
- Attribution: use directional models; avoid pretending multi-touch reports are perfect truth.
- Experiments: define hypothesis, sample, metric, guardrail, minimum duration, success threshold, and action rule.
- Data quality: track missing UTMs, duplicate leads, offline conversions, consent gaps, bot traffic, and CRM stage drift.

## Deliverable Shape

- Measurement questions
- Event/conversion schema
- UTM and source rules
- Dashboard outline
- Attribution assumptions
- Data QA checks
- Decision cadence

## References

- Read `references/analytics-attribution-checklist.md` when designing or auditing marketing measurement.
