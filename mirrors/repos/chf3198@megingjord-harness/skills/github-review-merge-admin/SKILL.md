---
name: github-review-merge-admin
description: Enforce review and merge administration gates with required checks, approvals, conversation resolution, rulesets, and merge queue readiness.
argument-hint: [mode: pre-review|pre-merge|admin-audit] [scope: repo|org] [policy-profile: strict|standard|light]
user-invocable: true
disable-model-invocation: false
---

# GitHub Review Merge Admin

## Purpose

Provide deterministic review and pre-merge governance checks.

## Core checks

- Required reviewers/approvals satisfied
- Required status checks green on latest commit
- Review conversations resolved
- Rulesets/branch protection satisfied
- Merge method/queue policy compliance

## Output format

```text
REVIEW_MERGE_ADMIN_REPORT
mode: <pre-review|pre-merge|admin-audit>
scope: <repo|org>
policy_profile: <strict|standard|light>
findings:
- <check status + evidence>
actions:
1) <action + owner + verification>
decision:
- <apply|defer|NO_CHANGE>
missing_evidence:
- <none or artifacts>
```
