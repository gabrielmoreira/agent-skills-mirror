---
name: analytics-instrumentation-plan
description: Plan analytics instrumentation for product, web, backend, funnel, and business events. Use when Codex is asked to define events, properties, user/account identity, tracking specs, validation, QA, or data quality for analytics.
license: MIT
---

# Analytics Instrumentation Plan

## Core Workflow

1. Identify decisions and analyses the instrumentation must support.
2. Define events, properties, identity keys, account/user relationships, source
   systems, and naming conventions.
3. Map events to product states, backend actions, UI flows, and funnel steps.
4. Add privacy, consent, PII, retention, and access considerations.
5. Specify validation, QA, backfill, and monitoring checks.
6. Document ownership and change-control process.

## Safety Rules

- Do not collect PII, sensitive data, or regulated data without explicit policy
  and reviewer approval.
- Do not invent platform-specific event behavior without checking current docs
  when implementation depends on it.
- Do not treat unvalidated instrumentation as reliable for decisions.

## Deliverable Shape

For instrumentation plans, provide:

- Decision and analysis goals
- Event taxonomy
- Property schema
- Identity and account model
- Privacy and consent notes
- Validation and QA plan
- Data quality monitoring
- Ownership and change control

## References

- Read `references/analytics-instrumentation-plan-checklist.md` when planning
  analytics tracking.
