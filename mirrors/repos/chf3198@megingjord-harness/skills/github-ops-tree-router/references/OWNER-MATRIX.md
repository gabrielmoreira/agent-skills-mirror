# GitHub Ops Skill Tree — Owner Matrix

## Primary router owner
- `github-ops-tree-router`: canonical routing owner for GitHub workflow requests.

## Adjacent router (non-GitHub workflow)
- `repo-standards-router`: canonical router for app-type standards composition only.
- Must hand off to `github-ops-tree-router` for GitHub workflow governance controls.

## Policy catalog owner
- `github-ops-excellence`: control catalog and policy-profile calibration (`strict|standard|light`).

## Capability gate owner
- `github-capability-resolver`: validates supportability by plan/visibility/owner/settings before execution.

## Delegated specialists
- `github-ticket-lifecycle-orchestrator`: intake→closeout lifecycle phases.
- `github-projects-agile-linkage`: issue types, sub-issues, dependencies, projects automations.
- `github-review-merge-admin`: review/check/ruleset/merge queue readiness.
- `github-release-incident-flow`: release gate, rollback, and incident follow-up controls.
- `github-ruleset-architecture`: ruleset layering, bypass posture, staged enforcement, merge queue compatibility.
- `github-actions-security-hardening`: actions token/pinning/OIDC/runner hardening controls.
- `repo-profile-governance`: repository profile/community health governance.
- `workflow-self-anneal`: workflow drift/failure hardening.

## Anti-overlap rule
If recommendations conflict, `github-ops-excellence` resolves policy profile and records rationale.
Execution remains with specialist skill owners.

Routing overlap is not allowed:
- Use `repo-standards-router` for standards branch selection.
- Use `github-ops-tree-router` for GitHub workflow lifecycle/review/release/security/ruleset operations.
