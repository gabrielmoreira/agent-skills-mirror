---
name: experiment-design-validation
description: Design, evaluate, and document experiments, A/B tests, product tests, growth tests, validation tests, hypotheses, primary metrics, guardrails, sample considerations, decision rules, and learning plans. Use when Codex is asked to test an idea, validate a change, run an experiment, compare variants, or create an experimentation plan.
license: MIT
---

# Experiment Design Validation

## Core Workflow

1. Define the decision the experiment will inform.
2. Write a falsifiable hypothesis with target audience, change, expected behavior, and reason.
3. Choose method: A/B test, holdout, fake-door test, concierge test, prototype test, usability test, smoke test, survey, landing-page test, or qualitative validation.
4. Define primary metric, guardrail metrics, segmentation, exposure rules, sample/traffic constraints, duration, and stop criteria.
5. Plan instrumentation and QA before launch.
6. Decide in advance how results will be interpreted and what action follows.
7. Record result, learning, caveats, and next experiment.

## Freshness Rule

Verify current analytics, experimentation platform, privacy, consent, and ad-platform docs before giving tactical setup guidance for A/B tools, GA4/Firebase events, conversion tracking, targeting, or experiment allocation.

## Deliverable Shape

For experiment work, provide:

- Decision and hypothesis
- Target audience and eligibility
- Variant/control design
- Primary and guardrail metrics
- Instrumentation and QA plan
- Duration/sample considerations
- Decision rules and follow-up actions

## References

- Read `references/experiment-design-checklist.md` when designing or reviewing an experiment.
