---
name: github-ruleset-architecture
description: Design and audit repository and organization ruleset architecture, including layering, bypass controls, enforcement modes, and merge queue compatibility.
argument-hint: "[mode: audit|design|migrate|verify] [scope: repo|org] [policy-profile: strict|standard|light]"
user-invocable: true
disable-model-invocation: false
---

# GitHub Ruleset Architecture

## Purpose

Create a deterministic, auditable protection model using GitHub rulesets as primary governance controls.

## Scope

- Branch/tag rulesets
- Push rulesets where supported
- Ruleset layering with existing branch protection
- Bypass actor minimization
- Merge queue compatibility checks

## Hard constraints

1. No destructive migration in one pass.
2. Preserve current enforcement unless explicitly approved.
3. Prefer staged rollout: `Disabled` -> validate -> `Active`.
4. Always report bypass principals explicitly.

## Core checks

- Ruleset target patterns (fnmatch) are precise and non-overlapping where possible.
- Layered rules produce intended effective policy (most restrictive wins).
- Bypass is least-privilege (role/team/app, justified).
- Merge queue requirements align with rules/protections.
- Required checks include `merge_group` readiness where merge queue is used.

## Output contract

```text
RULESET_ARCHITECTURE_REPORT
mode: <audit|design|migrate|verify>
scope: <repo|org>
policy_profile: <strict|standard|light>

current_state:
- rulesets_found: <count>
- branch_protection_found: <yes|no>
- merge_queue_required: <yes|no>

findings:
- id: R1
  result: <pass|fail|partial>
  observation: <what exists>
  risk: <low|medium|high>

proposed_changes:
1) change: <specific rule/ruleset>
   rationale: <why>
   rollout: <disabled-validate-active|direct>
   verification: <objective check>

decision:
- <apply|defer|NO_CHANGE>

missing_evidence:
- <none or required artifacts>
```

## Invocation policy

Use before pre-merge governance hardening and before introducing merge queue/ruleset changes across repos.
