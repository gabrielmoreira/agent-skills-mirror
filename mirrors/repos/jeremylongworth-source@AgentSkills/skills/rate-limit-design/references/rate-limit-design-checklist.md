# Rate Limit Design Checklist

## Inputs

- Protected endpoint or resource
- Expected traffic
- Client types
- Tenant model
- Account plans
- Abuse cases
- SLA or support constraints

## Policy

- Dimension
- Limit
- Window or algorithm
- Burst allowance
- Retry behavior
- Headers
- Error contract
- Exemptions
- Monitoring
- Override process

## Tests

- Under limit
- At limit
- Over limit
- Burst recovery
- Per-tenant isolation
- Retry-after behavior
