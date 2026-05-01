# PR Review Checklist

## Review Inputs

- Change summary and linked issue
- Diff or modified files
- Test plan and test output
- Screenshots, logs, or reproduction evidence when relevant
- Release notes, migrations, flags, or rollout plan

## Risk Areas

- Incorrect behavior or missed edge cases
- Backward compatibility and data migration
- Auth, permission, privacy, or secret-handling changes
- Error handling, retries, idempotency, and concurrency
- Performance, caching, memory, and query cost
- Observability, logging, and alerting
- Test coverage and manual verification

## Finding Quality

- Each finding names the risk and impact.
- Each finding points to concrete evidence.
- Suggested fixes are scoped and practical.
- Non-blocking improvements are clearly marked.
