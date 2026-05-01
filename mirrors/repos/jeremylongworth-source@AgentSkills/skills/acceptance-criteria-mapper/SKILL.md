---
name: acceptance-criteria-mapper
description: Turn skill, bundle, feature, or workflow goals into testable acceptance criteria. Use when Codex is asked to define pass/fail checks, map requirements to verification steps, or make a skill evaluation measurable.
license: MIT
---

# Acceptance Criteria Mapper

## Core Workflow

1. Identify the artifact, audience, and decision the criteria must support.
2. Convert broad goals into observable pass/fail checks.
3. Separate required behavior, optional quality signals, and out-of-scope
   expectations.
4. Add evidence requirements for each criterion: file, output, test, reviewer
   note, citation, trace, or command result.
5. Include safety and refusal criteria for high-risk workflows.
6. Flag criteria that are too subjective, too broad, or dependent on private
   data.

## Safety Rules

- Do not convert legal, financial, medical, security, or employment judgment
  into automatic approval criteria.
- Do not mark criteria satisfied without evidence.
- Do not use vague criteria such as "looks good" without observable checks.

## Deliverable Shape

For criteria maps, provide:

- Artifact and audience
- Required acceptance criteria
- Optional quality criteria
- Evidence required
- Safety/refusal criteria
- Open assumptions
- Validation method

## References

- Read `references/acceptance-criteria-mapper-checklist.md` when turning goals
  into measurable checks.
