---
name: qa-test-strategy
description: Design, audit, and improve QA and test strategy for software, games, websites, products, and launches. Use when Codex is asked about test plans, acceptance tests, regression, smoke testing, exploratory testing, automation scope, risk-based coverage, test data, release gates, defect triage, QA checklists, or verification strategy.
license: MIT
---

# QA Test Strategy

## Core Workflow

1. Identify the product surface, user risks, technical risks, release stage, platforms, integrations, and failure cost.
2. Define test goals by risk, not by a generic test pyramid alone.
3. Choose test types: unit, integration, contract, end-to-end, visual, accessibility, performance, security, compatibility, exploratory, playtest/usability, smoke, or regression.
4. Define acceptance criteria and release gates before implementation is considered done.
5. Plan test data, environments, mocks, fixtures, devices, accounts, permissions, and observability.
6. Separate automation candidates from manual/exploratory coverage.
7. Track defects by severity, reproducibility, affected users, release risk, and owner.

## Freshness Rule

Verify current framework, platform, browser, device, app-store, engine, or compliance testing requirements before giving version-sensitive QA guidance. Testing principles are durable; certification, browser behavior, and tool APIs change.

## Deliverable Shape

For QA work, provide:

- Scope and risk profile
- Test strategy by layer/type
- Acceptance criteria
- Test data and environment needs
- Automation vs manual coverage
- Release gates
- Defect triage and residual risk

## References

- Read `references/qa-test-strategy-checklist.md` when planning or reviewing QA coverage.
