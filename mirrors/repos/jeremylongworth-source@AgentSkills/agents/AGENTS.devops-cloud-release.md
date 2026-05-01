Use local skills as the primary routing layer for DevOps, cloud, and release
work.

Use `deployment-plan` when preparing deployment runbooks, rollout steps, smoke
tests, monitoring, owners, approvals, and go/no-go criteria.

Use `ci-workflow-plan` when designing CI jobs, triggers, quality gates, caches,
artifacts, secrets, permissions, and required checks across CI hosts.

Use `containerization-plan` when planning or reviewing container images,
runtime config, healthchecks, volumes, logs, and container security.

Use `environment-config-review` when reviewing env vars, config files, secrets,
feature flags, environment parity, validation, and drift.

Use `rollback-plan` when defining rollback triggers, recovery steps, fallback
paths, data restore needs, validation, and communication.

Use `cloud-cost-review` when reviewing hosting, cloud, storage, CI, logs,
traces, database, and managed-service cost risk.

Use `production-readiness-review` for go/no-go readiness, blockers, warnings,
evidence, owner approvals, support handoff, and release gates.

Use `release-risk`, `release-launch-readiness`, `skill-threat-model`, and
`concise-technical-writing` for broader launch, risk, security, and reporting
support.

Default to plan and review outputs. Do not deploy, change production config,
run migrations, rotate secrets, change live rate limits, delete resources, or
push images without explicit approval.
