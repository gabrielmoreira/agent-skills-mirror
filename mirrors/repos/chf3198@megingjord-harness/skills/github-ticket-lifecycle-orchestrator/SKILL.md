---
name: github-ticket-lifecycle-orchestrator
description: Naming conventions and phase protocol for GitHub ticket lifecycle. Baton workflow in manager-ticket-lifecycle.
argument-hint: [phase: intake|planning|execution|pre-pr|review|merge|closeout]
user-invocable: true
disable-model-invocation: false
---

# GitHub Ticket Lifecycle Orchestrator

## Hard constraints

1. No unbounded loops. Max one lifecycle pass per invocation.
2. If required evidence is missing, return `NO_CHANGE` with missing artifacts.
3. Do not claim merge/closeout success without verification evidence.

## Issue title format — plain imperative

`<Imperative verb phrase describing the desired outcome>` [≤ 72 chars]

- Start with imperative verb: "Fix", "Add", "Normalize", "Audit", "Stabilize"
- Plain English, human-scannable in boards and notifications
- **No `type(scope):` prefix** — type/scope expressed via labels
- No bracket tags `[BUG]`, no parallel IDs `TICKET-NNN`

Good: `Fix header nav contrast on dark hero backgrounds`
Bad: ~~`fix(nav): fix header nav contrast`~~ ~~`TICKET-008: Fix header`~~

## Commit and PR title format — Conventional Commits

`<type>(<scope>): <imperative description>` [≤ 72 chars]

Types: `feat` `fix` `chore` `content` `perf` `refactor` `docs` `style` `test`

## Branch naming

`<type>/<issue-number>-<short-slug>` — e.g. `fix/5-nav-contrast`, `feat/11-footer-redesign`

## Template requirements

Every repo must have `.github/ISSUE_TEMPLATE/` with at minimum: bug, task, epic forms.
Config: `blank_issues_enabled: false`. Plus `PULL_REQUEST_TEMPLATE.md` with issue linkage.

## Phase protocol (compact)

| Phase | Key actions |
|---|---|
| **intake** | Validate issue, apply labels/priority/milestone |
| **planning** | Split to sub-issues, add dependencies, set project fields |
| **execution** | One branch per ticket, link in Development panel, atomic commits |
| **pre-pr** | PR links issue with closing keywords, test evidence attached |
| **review** | Resolve feedback, re-run checks after changes |
| **merge** | Required reviews/checks satisfied, merge per repo policy |
| **closeout** | Issue state transition, branch deletion, post-merge cleanup |

## Label taxonomy reference

See `manager-ticket-lifecycle` for full label taxonomy:
`type:*`, `status:*`, `priority:*`, `area:*`, `role:*`

## Output format

```text
TICKET_LIFECYCLE_REPORT
phase: <phase>
scope: <repo|org>
policy_profile: <strict|standard|light>
checks:
- id: C1
  result: <pass|fail|partial>
  observation: <finding>
actions:
1) priority: <P1|P2|P3>
   owner: <role>
   change: <action>
decision: <apply|defer|NO_CHANGE>
missing_evidence: <none or list>
```
