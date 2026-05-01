---
name: github-capability-resolver
description: Resolve GitHub feature availability and policy constraints by plan, repo visibility, account type, and enabled settings before recommending governance actions.
argument-hint: "[scope: repo|org|enterprise] [visibility: public|private|internal] [plan: free|pro|team|enterprise] [surface: repo|actions|security|projects|merge-queue]"
user-invocable: true
disable-model-invocation: false
---

# GitHub Capability Resolver

## Purpose

Prevent invalid guidance by mapping requested controls to what is actually supported and enabled.

## Required inputs

- Repository owner type: user vs organization
- Visibility: public/private/internal
- Plan tier: free/pro/team/enterprise
- Surface intent: rulesets, merge queue, projects, security, actions
- Current repo/org settings where available

If any required input is missing, return `NO_CHANGE` with missing artifacts.

## Core checks

1. Determine capability support by plan + visibility + owner type.
2. Determine if feature is enabled in settings (repo/org).
3. Classify recommendation as:
   - `available-now`
   - `available-with-config-change`
   - `available-with-plan-upgrade`
   - `not-supported`
4. Provide lowest-friction valid alternative when unsupported.

## Output contract

```text
CAPABILITY_RESOLUTION_REPORT
scope: <repo|org|enterprise>
visibility: <public|private|internal>
plan: <free|pro|team|enterprise>
surface: <repo|actions|security|projects|merge-queue>

capabilities:
- id: <capability>
  status: <available-now|available-with-config-change|available-with-plan-upgrade|not-supported>
  evidence: <setting/doc/observation>
  constraints: <none|list>
  fallback: <none|recommended alternative>

decision:
- <apply|defer|NO_CHANGE>

missing_evidence:
- <none or required artifacts>
```

## Invocation policy

Run this skill first for any governance request that includes rulesets, merge queue, security features, or organization-wide controls.
