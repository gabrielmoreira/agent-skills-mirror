# Auth Flow Design Checklist

## Actors

- Anonymous user
- Authenticated user
- Admin
- Service account
- Integration partner
- Internal operator

## Flow Elements

- Login
- Token/session creation
- Refresh
- Logout/revocation
- Permission lookup
- Tenant boundary
- API key/service access
- Audit events
- Failure states

## Review Checks

- Least privilege
- Server-side authorization
- Token expiry and rotation
- Secret storage
- Tenant isolation
- Abuse cases
- Tests for denied access
- Provider facts verified when current details matter
