---
name: github-ops-excellence
description: Define and apply expert GitHub policy profiles and control catalogs used by specialized execution skills across ticketing, review/merge, governance, and release flows.
argument-hint: [mode: triage|refinement|pre-pr|pre-merge|sprint-health|release-readiness|incident-flow|admin-audit] [scope: repo|team|org|enterprise] [policy-profile: strict|standard|light]
user-invocable: true
disable-model-invocation: false
---

# GitHub Ops Excellence

## Purpose

Provide a bounded, auditable policy and control catalog for high-quality GitHub execution across repositories.

## Hard constraints

1. No unbounded loops or recursive retries.
2. Maximum one full pass per invocation.
3. Maximum ten actionable recommendations per invocation.
4. No silent policy changes; propose changes with rationale.
5. No bypass escalation without explicit approval trail.
6. If required evidence is missing, return `NO_CHANGE` with missing artifacts.

## Modes

- `triage`: issue quality and planning readiness.
- `refinement`: backlog readiness and dependency hygiene.
- `pre-pr`: branch hygiene and PR preparation.
- `pre-merge`: review/check/ruleset merge readiness.
- `sprint-health`: flow health, WIP risk, and review throughput.
- `release-readiness`: release gate and rollback readiness.
- `incident-flow`: containment-to-follow-up issue flow during production incidents.
- `admin-audit`: governance/ruleset/admin posture review.

## Scope boundary (catalog ownership)

This skill is the **policy catalog owner**, not the primary executor.

Primary execution belongs to specialist skills selected by `github-ops-tree-router`.

This skill provides:

- policy-profile calibration (`strict|standard|light`)
- shared control definitions
- severity and verification standards
- conflict resolution guidance when specialists disagree

This skill is **not** the primary owner for repository profile/discoverability hygiene
(topics, homepage, social preview, community health file completeness). Delegate those to `repo-profile-governance`.

## Invocation order

1. For plan/feature-sensitive controls, run `github-capability-resolver` first.
2. Run `github-ops-tree-router` to select execution skill(s).
3. Apply `github-ops-excellence` as profile overlay to calibrate strictness and evidence requirements.

## Shared control packs by mode

### triage

- Issue title is a plain imperative sentence ≤72 chars — no `type(scope):` prefix (Conventional Commits belongs on commits/PRs, not issues).
- Issue title has no pseudo-prefixes (`[BUG]`, `[P1]`, `TICKET-123`, `JIRA-123`) and does not duplicate type in the title when a `type:*` label exists.
- GitHub `#N` is used as canonical ID; no parallel local ID schemes (`TICKET-NNN`, bracket tags, etc.) present.
- Issue includes: problem, expected outcome, acceptance criteria.
- Metadata includes: assignee, labels (priority + area + type), milestone/iteration, project link.
- Large work is decomposed with sub-issues/dependencies.
- Template/form adherence is verified; `blank_issues_enabled: false` confirmed in repo.

### refinement

- Backlog item has definition-of-ready (scope, acceptance, dependencies, risk).
- Parent/child issue relationships are coherent (sub-issues, dependencies).
- Priority and iteration fields are populated.
- Blocked work has explicit owner and next action.

### pre-pr

- One branch per concern.
- PR links issue(s) and states test evidence.
- PR template fields completed.
- Reviewers and code owners requested where applicable.

### pre-merge

- Required reviews satisfied.
- Required status checks passing on latest commit.
- Conversation resolution complete.
- Ruleset/branch-protection requirements satisfied.
- If merge queue is required, CI supports `merge_group` trigger.

### sprint-health

- WIP is within agreed team limits.
- Aged items are identified with owner and resolution plan.
- PR review latency and merge latency are measured against team targets.
- Blocked-item ratio is tracked and triaged.

### release-readiness

- Changelog/release notes prepared.
- Release evidence links present (tests/checks/artifacts).
- Rollback or remediation path documented.
- No unresolved blocking issues for target milestone.

### incident-flow

- Incident item includes severity, impact, owner, and containment plan.
- Hotfix branch/PR is linked to incident issue and validation evidence.
- Rollback trigger and rollback owner are explicit.
- Follow-up issues (root cause, prevention, docs/tests) are created before closure.

### admin-audit

- Rulesets/protection target critical branches.
- CODEOWNERS coverage exists for protected paths (deep ownership hygiene belongs to `repo-profile-governance`).
- Bypass list is minimal and justified.
- Ruleset history/insights reviewed for drift.
- Security gates (code scanning/dependency review) enforced where required.

### actions-security

- `GITHUB_TOKEN` least privilege baseline is enforced.
- Third-party actions pinning policy is enforced.
- OIDC is preferred for cloud auth over long-lived static secrets.
- Workflow ownership is protected (`.github/workflows/` under CODEOWNERS).
- Runner trust boundaries are documented and policy-compliant.

## Output format (required)

```text
GITHUB_OPS_POLICY_REPORT
mode: <triage|refinement|pre-pr|pre-merge|sprint-health|release-readiness|incident-flow|admin-audit>
scope: <repo|team|org|enterprise>
policy_profile: <strict|standard|light>

controls:
- id: F1
  severity: <low|medium|high>
  area: <ticketing|branching|pr|governance|security|release|projects|actions-security>
  control: <policy control statement>
  strict: <requirement>
  standard: <requirement>
  light: <requirement>

calibration_actions:
1) priority: <P1|P2|P3>
  executor_skill: <selected specialist>
  profile_adjustment: <specific calibration>
  verification: <objective pass condition>

metrics_snapshot:
- metric: <lead-time|cycle-time|review-latency|merge-latency|blocked-age|wip|reopen-rate>
  observed: <value>
  target: <value>
  status: <ok|breach>

decision:
- <apply|defer|NO_CHANGE>

missing_evidence:
- <none or required artifacts>
```

## Evidence requirements

Collect only artifacts relevant to mode and selected specialist path:

- Issues/PR metadata
- Branch and ruleset/protection settings
- Check run results and review states
- Project field/status snapshots
- Project insights/charts or equivalent flow snapshot
- Release notes and milestone status

## Stop conditions

Return `NO_CHANGE` when:

- Evidence is incomplete for the selected mode.
- Recommendation cannot be objectively verified.
- Proposed change would reduce required safety controls.
- Same recommendation was recently applied and verified.
- Metrics are unavailable and no reliable proxy exists.

## Quality bar

A valid result must be:

- Specific (not generic)
- Testable (clear pass/fail)
- Minimal (least disruptive change)
- Traceable (links finding to action)
