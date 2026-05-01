---
name: accessibility-test-plan
description: Plan accessibility tests for web, app, game, document, and workflow experiences. Use when Codex is asked to define keyboard, screen reader, contrast, focus, ARIA, reduced motion, captions, forms, or WCAG-oriented validation.
license: MIT
---

# Accessibility Test Plan

## Core Workflow

1. Identify experience, users, assistive technologies, target platforms, and
   applicable accessibility standard or internal policy.
2. Define keyboard, focus, semantics, names/roles/values, contrast, motion,
   captions, forms, error, and responsive checks.
3. Separate automated checks from manual screen reader and keyboard testing.
4. Include test data, viewport/device coverage, and severity rules.
5. Record evidence, blockers, and remediation ownership.
6. Recommend release gate based on user impact.

## Safety Rules

- Do not claim WCAG compliance from automated checks alone.
- Do not use accessibility overlays or superficial fixes as proof.
- Escalate blockers that prevent core task completion by keyboard or assistive
  technology.

## Deliverable Shape

For accessibility test plans, provide:

- Scope and standard
- Automated checks
- Manual keyboard and screen reader checks
- Visual and motion checks
- Forms and error checks
- Severity and release gates
- Evidence and remediation owner

## References

- Read `references/accessibility-test-plan-checklist.md` when planning
  accessibility validation.
