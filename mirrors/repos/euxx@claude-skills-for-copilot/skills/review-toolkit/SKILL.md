---
name: review-toolkit
description: Orchestrates a comprehensive code review using up to 6 specialist skills. Dispatches code-review, code-simplifier, comment-analyzer, silent-failure-hunter, type-design-analyzer, and test-analyzer based on the scope of changes. Use for thorough end-to-end review of code changes.
argument-hint: "[file, directory, or git diff to review]"
user-invocable: true
---

# Review Toolkit

Comprehensive code review orchestrator. Dispatches specialist review agents based on the scope of changes and aggregates all findings in a unified report.

## Specialist Skills

| Skill                     | Purpose                                                         |
| ------------------------- | --------------------------------------------------------------- |
| **code-review**           | Bugs, security issues, correctness, conventions-file violations |
| **code-simplifier**       | Unnecessary complexity, duplication, readability                |
| **comment-analyzer**      | Comment accuracy, comment rot, misleading documentation         |
| **silent-failure-hunter** | Silent errors, inadequate user feedback, catch block quality    |
| **type-design-analyzer**  | Type encapsulation, invariant expression and enforcement        |
| **test-analyzer**         | Behavioral coverage gaps, test quality, anti-pattern detection  |

## Dispatch Rules

Always run:

- **code-review** — applies to any code change

Run when applicable:

- **test-analyzer** — test files modified or new behavior added
- **silent-failure-hunter** — error handling code modified (`try/catch`, error callbacks, fallbacks)
- **type-design-analyzer** — new types, interfaces, or data models added or significantly changed
- **comment-analyzer** — documentation comments or inline comments added/modified

Run after correctness is confirmed (regardless of other findings):

- **code-simplifier** — once critical bugs and coverage gaps are resolved

## Process

1. Identify the scope of changes (files changed, types of changes)
2. Determine which specialist skills to dispatch based on the rules above
3. Run each selected skill as a sub-agent against the relevant scope
4. Collect all findings
5. Aggregate into a unified report

## Output Format

```
## Toolkit Summary
Specialists dispatched: [list]
Overall assessment: [PASS / NEEDS WORK / CRITICAL ISSUES]

## Critical Issues
[Aggregated CRITICAL findings from all specialists, with source skill noted]

## Important Issues
[Aggregated HIGH/IMPORTANT findings]

## Suggestions
[Aggregated MEDIUM/lower priority findings]

## Positive Observations
[Notable good practices found across all reviews]
```

Severity order: Critical → Important → Suggestions → Positive Observations.
