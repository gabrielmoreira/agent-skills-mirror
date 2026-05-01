# Phase 3 Migration — De-overlap with repo-standards-router

## Goal

Remove GitHub workflow-routing overlap from `repo-standards-router` while preserving standards classification behavior.

## Effective behavior after Phase 3

- `repo-standards-router` selects app-type standards branches and overlays.
- `repo-standards-router` emits a handoff block when workflow governance controls are requested.
- `github-ops-tree-router` is the only router for GitHub workflow operations.

## Trigger conditions for handoff

Set handoff required when request includes one or more:

- ticket lifecycle / PR governance flow
- review or merge gate administration
- rulesets / branch-protection architecture
- merge queue readiness
- Actions hardening (token, pinning, OIDC, runner trust)

## Migration checklist

1. Update prompts/playbooks that previously called `repo-standards-router` for GitHub lifecycle tasks.
2. Route GitHub workflow goals through `github-ops-tree-router`.
3. Keep `repo-standards-router` usage for app-type standards selection only.
4. Validate one public and one private repository invocation path.

## Validation expectations

- No direct lifecycle/review/release/actions/ruleset execution recommendations are produced by `repo-standards-router`.
- Handoff recommendations from `repo-standards-router` target `github-ops-tree-router` only.
- Router reports remain deterministic with `decision` and `missing_evidence` populated.
