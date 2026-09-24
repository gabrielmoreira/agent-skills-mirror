# Regression Check Checklist

## Changed Surface

- User-facing behavior
- API contract or schema
- Auth, permissions, billing, or data handling
- Background jobs, queues, scheduled tasks, or integrations
- Configuration, flags, environment, or deployment behavior
- Documentation, onboarding, or support workflow

## Coverage Types

Select coverage for the changed behavior and plausible side effects. This is
a menu, not a requirement to run every type of test.

- Unit or component tests
- Integration and contract tests
- End-to-end smoke tests
- Manual exploratory checks
- Visual and accessibility checks
- Performance and load checks
- Migration, rollback, and compatibility checks

## Gate Checks

- Is the original issue reproducible or represented by a failing test?
- Does the new coverage fail for the old behavior and pass for the fix?
- Are affected adjacent workflows covered?
- Have the relevant checks and repository gates passed without a reason to
  broaden or repeat them?
- Is there a rollback or mitigation if regression appears in production?
