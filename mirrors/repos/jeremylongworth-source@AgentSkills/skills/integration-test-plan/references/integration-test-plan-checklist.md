# Integration Test Plan Checklist

## Boundaries

- API to service
- Service to database
- Service to queue
- Auth provider
- External API adapter
- File/storage system
- Background job

## Cases

- Success
- Validation failure
- Permission denied
- Dependency failure
- Retry/recovery
- Persistence
- Contract mismatch
- Cleanup

## Environment

- Test database
- Fake service
- Containerized dependency
- Seed data
- Cleanup strategy
- CI command
