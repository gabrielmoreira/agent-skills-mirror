# Release Risk Checklist

## Scope

- Features, fixes, migrations, and configuration changes
- Affected users, plans, regions, platforms, and integrations
- Deployment method, timing, dependencies, and owner

## Readiness Evidence

- Test results and known gaps
- Code review and required approvals
- Migration rehearsal or rollback plan
- Feature flags, staged rollout, or kill switch
- Monitoring, alerts, logs, and dashboard links
- Support notes, docs, and customer communication plan

## Go/No-Go Checks

- Are severity-one and severity-two risks mitigated or accepted by an owner?
- Is rollback possible and tested enough for the risk?
- Are support and incident owners ready?
- Are data quality, auth, billing, and security risks reviewed?
- Is the release window appropriate for the blast radius?
