---
name: release-launch-readiness
description: Plan, audit, and execute release and launch readiness for software, games, websites, products, campaigns, and public launches. Use when Codex is asked about release checklists, launch plans, deployment risk, feature flags, rollout plans, rollback plans, monitoring, support readiness, communications, incident response, post-launch review, or go-live readiness.
license: MIT
---

# Release Launch Readiness

## Core Workflow

1. Identify what is launching, who is affected, release surface, risk level, dependencies, timing, and rollback constraints.
2. Separate deploy, release, and launch. Code can be deployed before a feature is released or marketed.
3. Define readiness gates: QA, security/privacy, accessibility, performance, analytics, documentation, support, legal/compliance, billing, and communications.
4. Plan rollout: internal, beta, cohort, percentage, region, platform, feature flag, waitlist, or full launch.
5. Prepare rollback or mitigation: feature flag off, config rollback, build rollback, data migration plan, hotfix, support script, and owner.
6. Set monitoring and response: dashboards, alerts, logs, health metrics, business metrics, incident channel, escalation, and decision owner.
7. Run post-launch review with outcomes, incidents, learnings, and follow-up actions.

## Freshness Rule

Verify current deployment platform, marketplace, app-store, payment, compliance, and incident-management requirements before giving tactical release guidance. Release operations depend heavily on the actual stack and platform rules.

## Deliverable Shape

For release work, provide:

- Launch scope and risk profile
- Readiness checklist
- Rollout plan
- Rollback/mitigation plan
- Monitoring and support plan
- Communication plan
- Post-launch review criteria

## References

- Read `references/release-launch-checklist.md` when planning or auditing a release or launch.
