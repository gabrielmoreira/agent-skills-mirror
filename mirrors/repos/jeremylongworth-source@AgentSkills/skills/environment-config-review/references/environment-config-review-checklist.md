# Environment Config Review Checklist

## Inventory

- Local
- Test
- CI
- Preview
- Staging
- Production
- Secret store
- Feature flags

## Check

- Required variables
- Defaults
- Types
- Validation
- Missing-value behavior
- Deprecated settings
- Secret redaction
- Drift between environments
- Owner and rotation notes

## Risks

- Secret committed
- Production default unsafe
- Flag changes unreviewed
- CI differs from production
- Missing config crashes runtime
