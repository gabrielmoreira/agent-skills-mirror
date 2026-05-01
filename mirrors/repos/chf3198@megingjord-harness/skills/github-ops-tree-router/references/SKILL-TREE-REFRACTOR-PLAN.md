# GitHub Skill Tree Refactor Plan (v2)

## Objective

Reduce overlap, enforce capability-aware routing, and raise governance/security depth across all repositories (public and private).

## Keep / Merge / Deprecate

### Keep (execution skills)
- `github-ticket-lifecycle-orchestrator`
- `github-projects-agile-linkage`
- `github-review-merge-admin`
- `github-release-incident-flow`
- `repo-profile-governance`
- `workflow-self-anneal` (meta)

### Keep (router)
- `github-ops-tree-router` as the only GitHub workflow router.

### Convert
- `github-ops-excellence` -> policy/control catalog skill (non-primary executor).

### Add (new core skills)
- `github-capability-resolver`
- `github-ruleset-architecture`
- `github-actions-security-hardening`

### Deprecate routing overlap
- GitHub workflow routing behavior in `repo-standards-router` (retain repo-type standards routing only).

## Routing contract

1. Run `github-capability-resolver` first when request includes rulesets, merge queue, security features, org-wide controls, or private/public policy variance.
2. Run `github-ops-tree-router` second to select one primary execution path.
3. Run exactly one primary executor (+ one optional specialist where needed).
4. Run `workflow-self-anneal` only on trigger events (repeat failures, pre-merge hardening, post-release drift).

## Cross-skill output schema (required)

All GitHub skills return:
- `checks`
- `actions`
- `decision` (`apply|defer|NO_CHANGE`)
- `missing_evidence`

This ensures deterministic manager -> collaborator -> reviewer/admin handoff.

## Coverage upgrades required

- Rulesets layering, bypass minimization, staged enforcement status.
- Merge queue + CI `merge_group` readiness.
- Actions supply-chain hardening (pinning, token scope, OIDC, workflow CODEOWNERS, runner strategy).
- Community health defaults via account/org `.github` repository.
- Issue forms/template chooser and PR template governance.

## KPI set

- Lead time issue->merge
- Reopen rate
- Queue ejection/removal rate
- PR policy completeness rate
- Workflow SHA pinning rate
- Ruleset coverage rate
- Community profile completeness score

## Rollout

1. Add new skills (this step complete).
2. Update router references and invocation map.
3. Re-scope `github-ops-excellence` to catalog-only.
4. De-overlap `repo-standards-router` from GitHub workflow routing (Phase 3 complete).
5. Validate on one public and one private repository.

## Phase 3 artifacts

- `repo-standards-router/SKILL.md` scope boundary + handoff protocol
- `references/OWNER-MATRIX.md` cross-router ownership split
- `references/INVOCATION-MAP.md` cross-router handoff sequence
- `references/PHASE-3-DEOVERLAP-MIGRATION.md` migration checklist
