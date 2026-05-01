# Issue To Plan Checklist

## Inputs

- Original issue, ticket, bug report, or feature request
- Expected behavior and current behavior
- Reproduction steps, environment, version, and test data
- Affected user segment, severity, and business impact
- Related code, logs, tests, docs, incidents, and prior fixes

## Planning Checks

- What is the smallest useful change?
- Which modules, APIs, schemas, configuration, or docs may change?
- What existing behavior must be preserved?
- What data migration, permissions, or compatibility concerns exist?
- Which tests should fail before the fix and pass after it?
- What manual verification is still needed?

## Output Checks

- The plan separates facts from assumptions.
- Acceptance criteria are observable.
- Tests map directly to risks.
- Open questions are limited to decisions that materially affect scope.
