---
name: github-projects-agile-linkage
description: Apply Agile linkage controls in GitHub using issue types, sub-issues, dependencies, issue-branch/PR linkage, project fields, and built-in automations.
argument-hint: [mode: audit|plan|apply|verify] [scope: repo|org] [policy-profile: strict|standard|light]
user-invocable: true
disable-model-invocation: false
---

# GitHub Projects Agile Linkage

## Purpose

Operationalize Jira-like planning/linkage behavior natively on GitHub.

## Required controls

1. Issue taxonomy: issue types + labels.
2. Hierarchy: sub-issues for decomposition.
3. Dependencies: `blocked by` / `blocking` links.
4. Development linkage: issue ↔ branch and issue ↔ PR.
5. PR close linkage: closing keywords where appropriate.
6. Projects fields: status, priority, iteration, owner.
7. Built-in workflows: auto-add, status sync, auto-archive.

## Output format

```text
AGILE_LINKAGE_REPORT
mode: <audit|plan|apply|verify>
scope: <repo|org>
policy_profile: <strict|standard|light>
coverage:
- issue_types: <pass|fail|partial>
- sub_issues: <pass|fail|partial>
- dependencies: <pass|fail|partial>
- dev_linkage: <pass|fail|partial>
- project_fields: <pass|fail|partial>
- automations: <pass|fail|partial>
actions:
1) <action + owner + verification>
decision:
- <apply|defer|NO_CHANGE>
missing_evidence:
- <none or artifacts>
```
