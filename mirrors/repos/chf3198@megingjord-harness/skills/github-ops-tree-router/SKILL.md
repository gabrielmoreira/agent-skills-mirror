---
name: github-ops-tree-router
description: Route GitHub workflow requests through a capability-first GitHub skill tree with explicit ownership boundaries and minimal overlap.
argument-hint: [goal: ticket-lifecycle|agile-projects|review-merge|release-incident|repo-governance|actions-security|ruleset-architecture|process-hardening] [policy-profile: strict|standard|light]
user-invocable: true
disable-model-invocation: false
---

# GitHub Ops Tree Router

## Purpose

Select the correct specialized GitHub operations path with minimal overlap and valid feature support.

## Capability-first protocol

For goals involving rulesets, merge queue, Actions security, or plan-sensitive controls,
run `github-capability-resolver` first.

If capability status is `not-supported` or evidence is incomplete, return `NO_CHANGE`.

## Ownership model

- Primary router owner: `github-ops-tree-router`
- Policy catalog owner: `github-ops-excellence`
- Delegates:
  - `github-capability-resolver`
  - `github-ticket-lifecycle-orchestrator`
  - `github-projects-agile-linkage`
  - `github-review-merge-admin`
  - `github-release-incident-flow`
  - `github-ruleset-architecture`
  - `github-actions-security-hardening`
  - `repo-profile-governance`
  - `workflow-self-anneal`

## Routing table

- `goal=ticket-lifecycle` -> `github-ticket-lifecycle-orchestrator` (+ `github-ops-excellence` for policy profile)
- `goal=agile-projects` -> `github-projects-agile-linkage`
- `goal=review-merge` -> `github-capability-resolver` + `github-review-merge-admin`
- `goal=release-incident` -> `github-release-incident-flow` (+ `github-ops-excellence` for policy profile)
- `goal=repo-governance` -> `repo-profile-governance`
- `goal=actions-security` -> `github-capability-resolver` + `github-actions-security-hardening`
- `goal=ruleset-architecture` -> `github-capability-resolver` + `github-ruleset-architecture`
- `goal=process-hardening` -> `workflow-self-anneal`

## Required references

- [Owner Matrix](references/OWNER-MATRIX.md)
- [Invocation Map](references/INVOCATION-MAP.md)
- [Output Contracts](references/OUTPUT-CONTRACTS.md)
- [Phase 3 De-overlap Migration](references/PHASE-3-DEOVERLAP-MIGRATION.md)

## Output format

```text
GITHUB_OPS_ROUTER_REPORT
goal: <ticket-lifecycle|agile-projects|review-merge|release-incident|repo-governance|actions-security|ruleset-architecture|process-hardening>
policy_profile: <strict|standard|light>
capability_resolution:
- required: <yes|no>
- status: <available-now|available-with-config-change|available-with-plan-upgrade|not-supported|not-run>
selected_skill_path:
- <ordered skills>
ownership:
- router: github-ops-tree-router
- policy_catalog: github-ops-excellence
- delegates: <skills>
checks:
- <required verifications>
decision:
- <apply|defer|NO_CHANGE>
missing_evidence:
- <none or artifacts>
```
