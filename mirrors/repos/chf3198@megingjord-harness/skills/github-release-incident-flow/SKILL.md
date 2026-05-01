---
name: github-release-incident-flow
description: Govern release readiness and incident response flow in GitHub with rollback evidence, hotfix linkage, and follow-up controls.
argument-hint: [mode: release-readiness|incident-flow|post-incident] [scope: repo|org] [policy-profile: strict|standard|light]
user-invocable: true
disable-model-invocation: false
---

# GitHub Release Incident Flow

## Purpose

Standardize release and incident lifecycle controls in GitHub Issues/PRs/Projects.

## Core checks

- Release notes/changelog readiness
- Validation evidence linked to release item
- Rollback path and owner documented
- Incident severity/impact/owner/containment recorded
- Hotfix branch+PR linkage to incident
- Follow-up prevention tickets created before closure

## Output format

```text
RELEASE_INCIDENT_REPORT
mode: <release-readiness|incident-flow|post-incident>
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
