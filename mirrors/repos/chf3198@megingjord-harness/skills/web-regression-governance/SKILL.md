---
name: web-regression-governance
description: Apply non-bypass visual/DOM/runtime regression governance for website-static and web-app repositories that use HTML/CSS/JS runtime behavior.
argument-hint: [app-type: website-static|web-app|auto-detect] [strictness: strict|standard] [external-audits: required|optional]
user-invocable: true
disable-model-invocation: false
---

# Web Regression Governance

## Purpose

Establish enforceable regression protection for repositories where user-visible behavior is driven by HTML/CSS/JS (including runtime injection/DOM mutation patterns).

This skill defines controls that must block merges/releases when homepage or critical-route invariants regress.

## Applicability

Use for:

- `website-static` repositories.
- `web-app` repositories with SSR/SPA routes where visual ordering and runtime rendering matter.
- Any repo with HTML/CSS and route-specific runtime scripts that can mutate layout/visibility.

## Core controls (required)

1. **Fail-fast publish/runtime verification**
   - Runtime verification scripts must exit non-zero on invariant failures.
   - No warning-only mode for release-critical checks.

2. **Critical-route invariants**
   - Define route-specific assertions for primary pages (at minimum homepage + key conversion route).
   - Assert hero/headline/primary CTA presence where applicable.
   - Assert section-order constraints for above-the-fold safety.

3. **Runtime mutation guardrails**
   - Route-targeted scripts must be explicitly scoped to intended routes.
   - Add static checks that fail if scripts target forbidden routes (for example homepage mutations by service-page overrides).

4. **Visual/DOM regression gate in CI**
   - Run objective visual/DOM checks in CI for pull requests and merge-group paths.
   - Treat failures as blocking under strict profile.

5. **Non-bypass governance wiring**
   - Required checks must be wired so merges cannot proceed when regression gates fail.
   - Merge queue readiness must include regression gates.

6. **Evidence and provenance**
   - Record before/after evidence (screenshots and assertion output) for critical routes.
   - Keep release notes linked to exact check runs for traceability.

## Verification matrix

For each change touching HTML/CSS/runtime JS or publish scripts, require:

- Static invariant checks: route-scope and forbidden-pattern detection.
- Runtime assertions: presence/order/visibility checks on critical routes.
- Visual/DOM assertions: deterministic checks in CI.
- Release verification: final post-publish verification must hard-fail on drift.

## Output format (required)

```text
WEB_REGRESSION_GOVERNANCE_REPORT
repo_type: <website-static|web-app>
strictness: <strict|standard>
external_audits: <required|optional>

controls_status:
- fail_fast_runtime_verify: <present|missing>
- critical_route_invariants: <present|missing>
- runtime_route_scope_guards: <present|missing>
- ci_visual_dom_gate: <present|missing>
- non_bypass_required_checks: <present|missing>
- provenance_evidence: <present|missing>

required_changes:
1) <specific change>
   verification: <objective command/check>

risk_if_deferred:
- <high/medium/low with short reason>

decision:
- <apply|defer>
```

## Profile calibration

- `strict`: all six core controls required and blocking.
- `standard`: controls 1–4 required; 5–6 required for production-bound repos.

## Handoffs

- For repository classification and baseline selection, invoke `repo-standards-router` first.
- For branch protection, required checks, merge queue, and ruleset administration, hand off to `github-ops-tree-router`.
- Use `workflow-self-anneal` only after failure/process mismatch.
