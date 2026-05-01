# Error Handling Contracts Checklist

## Error Envelope

- Machine-readable code
- Client-safe message
- Details or field errors
- Correlation/request ID
- Retryable flag or guidance
- Documentation link
- Timestamp only if useful

## Error Classes

- Validation
- Authentication
- Authorization
- Not found
- Conflict
- Rate limit
- Dependency failure
- Timeout
- Internal error

## Review Checks

- No sensitive internals exposed
- Consistent status codes
- Client recovery path clear
- Logs contain diagnostics
- Tests cover common failures
