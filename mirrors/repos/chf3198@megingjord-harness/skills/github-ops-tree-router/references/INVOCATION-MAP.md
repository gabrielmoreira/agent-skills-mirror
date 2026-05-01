# Invocation Map

## Cross-router handoff (Phase 3)
1. `/repo-standards-router primary-type=<...> policy-profile=<...>`
2. If output `handoff.required=yes`, invoke:
	- `/github-ops-tree-router goal=<ticket-lifecycle|review-merge|release-incident|actions-security|ruleset-architecture|repo-governance> policy-profile=<...>`
3. Execute selected specialist path from `github-ops-tree-router`.

## Ticket kickoff
1. `/github-ops-tree-router goal=ticket-lifecycle policy-profile=standard`
2. `/github-ticket-lifecycle-orchestrator phase=intake`
3. `/github-ops-excellence mode=triage` (policy overlay)

## Agile planning
1. `/github-projects-agile-linkage mode=plan`
2. `/github-ticket-lifecycle-orchestrator phase=planning`

## Pre-PR
1. `/github-ops-tree-router goal=ticket-lifecycle policy-profile=standard`
2. `/github-ticket-lifecycle-orchestrator phase=pre-pr`
3. `/github-ops-excellence mode=pre-pr` (policy overlay)

## Pre-merge
1. `/github-capability-resolver scope=repo surface=merge-queue`
2. `/github-review-merge-admin mode=pre-merge`
3. `/github-ops-excellence mode=pre-merge` (policy overlay)

## Ruleset architecture
1. `/github-capability-resolver scope=repo surface=merge-queue`
2. `/github-ruleset-architecture mode=audit`

## Actions hardening
1. `/github-capability-resolver scope=repo surface=actions`
2. `/github-actions-security-hardening mode=audit`

## Release / incident
1. `/github-release-incident-flow mode=release-readiness|incident-flow`
2. `/github-ops-excellence mode=release-readiness|incident-flow` (policy overlay)

## Post-failure hardening
1. `/workflow-self-anneal context=post-failure scope=workflow`
