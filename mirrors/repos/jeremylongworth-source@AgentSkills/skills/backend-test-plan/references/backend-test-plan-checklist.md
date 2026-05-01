# Backend Test Plan Checklist

## Test Layers

- Unit
- Integration
- API contract
- Database/migration
- Auth and permission
- Error handling
- Rate limit
- Background job
- External dependency
- Performance/load
- Regression

## Coverage Questions

- What changed?
- What can fail silently?
- What data can be corrupted?
- What access can be denied or over-granted?
- What clients depend on this contract?
- What must pass before merge?
- What must pass before release?

## Evidence

- Test command
- Test file names
- Required fixtures
- Manual verification
- CI gate
- Rollback check
