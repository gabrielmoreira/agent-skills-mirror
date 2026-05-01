---
name: repo-standards-router
description: Classify a repository by app type and route it to the correct standards branch, policy profile, and verification gates.
argument-hint: [primary-type: website-static|web-app|library-sdk|infra-automation|auto-detect] [policy-profile: strict|standard|light] [overlays: security|collaboration|release|observability]
user-invocable: true
disable-model-invocation: false
---

# Repo Standards Router

## Purpose

Select the smallest correct standards stack for a repo, based on primary app type, overlapping overlays, and risk profile.

## Scope boundary

This skill is the router for **repository standards composition** (app-type + overlays), not the router for GitHub workflow governance.

- Owns: standards branch selection, verification gates, branch-promotion candidates.
- Does not own: ticket lifecycle execution, review/merge administration, ruleset architecture, merge queue readiness, Actions hardening.

If the request includes GitHub workflow governance controls, hand off to `github-ops-tree-router` after standards selection.

## Hard constraints

1. No broad policy rewrites in one pass.
2. Maximum 8 recommendations.
3. Must return explicit verification gates.
4. If repository type is unclear, return `NO_CHANGE` + missing evidence.
5. Prefer existing classes + overlays over creating a new branch.
6. For app-types with first-class versioned distribution channels, include a `version-selectability` control in release recommendations.

## Decision flow

1. Detect `primary_type` from runtime intent and repository artifacts.
2. Detect `secondary_types` only when overlap is clear and evidence-backed.
3. Apply `core-baseline` controls.
4. Apply primary-type controls from [APP-TYPE-SKILL-TREE.md](../APP-TYPE-SKILL-TREE.md).
5. Apply selected overlays (`security`, `collaboration`, `release`, optional `observability`).
6. Calibrate severity with `policy_profile`.
7. Emit actionable controls and checks.

## Handoff protocol

Set `handoff_required=yes` when any requested control includes:

- branch protection or rulesets,
- merge queue policy,
- Actions token/pinning/OIDC/runner hardening,
- ticket/PR lifecycle administration.

Then set `handoff_skill=github-ops-tree-router` and include a short reason.

## Output format (required)

```text
STANDARDS_ROUTER_REPORT
primary_type: <website-static|web-app|library-sdk|infra-automation>
secondary_types: <none|comma-separated types>
overlays: <none|security,collaboration,release,observability>
policy_profile: <strict|standard|light>
confidence: <high|medium|low>

selected_branches:
- core-baseline
- <primary-type-branch>
- <overlay-branches>

handoff:
- required: <yes|no>
- handoff_skill: <none|github-ops-tree-router>
- reason: <none|why governance routing is needed>

controls:
1) priority: <P1|P2|P3>
   area: <security|testing|docs|release|quality|accessibility|seo|supply-chain>
   change: <specific control>
   verification: <objective check>

missing_controls:
- <none or control gaps not yet covered by current branches>

skills_to_run_next:
- <none|web-regression-governance|repo-profile-governance|github-ops-tree-router|workflow-self-anneal>

decision:
- <apply|defer|NO_CHANGE>

missing_evidence:
- <none or required artifacts>

evolution_todos:
- <only if repeated gaps suggest future branch creation>
```

## App-type branch controls (summary)

- `website-static`: SEO/schema sync, visual regression, responsive QA, WCAG AA baseline, performance budgets; run `web-regression-governance` when runtime injection/DOM mutation risks exist.
- `web-app`: component/e2e testing, auth/session hardening, dependency controls, WCAG AA; run `web-regression-governance` for route-level visual/DOM/runtime invariant enforcement.
- `library-sdk`: compatibility policy, SemVer, changelog quality, consumer examples.
- `infra-automation`: least privilege, pinned dependencies/actions, policy checks, runbooks.

## Overlays (summary)

- `security`: secrets/dependency checks, hardening and incident-readiness controls.
- `collaboration`: contributor-facing hygiene (`LICENSE`, `CONTRIBUTING`, `CODE_OF_CONDUCT`, `SECURITY`, templates, CI).
- `release`: SemVer/release checklist, changelog quality, rollback notes.
- `observability` (optional): telemetry, SLO/error budget, alert ownership.

## Version-selectability capability rule (required)

When `overlays` includes `release`, evaluate whether the repository's distribution channel supports exact version installation or pinning (for example package registries, extension marketplaces, container tags/digests, action tags).

If supported, add a required release control that enforces all of the following:

1. Immutable per-version artifacts (no overwrite of released versions).
2. Exact-version install path remains available for supported historical versions.
3. Release pipeline verifies exact-version installability before marking a version active/announced.
4. Update prompts use the same canonical version source used for installation.

If not supported by platform constraints, record an explicit exception and the nearest deterministic fallback.

## Future branch promotion rule

Recommend adding a new branch only if all are true:

1. Repeated need appears in at least 2 repositories.
2. At least 3 controls are not covered by existing primary types + overlays.
3. Risk is meaningful if left as ad-hoc guidance.
