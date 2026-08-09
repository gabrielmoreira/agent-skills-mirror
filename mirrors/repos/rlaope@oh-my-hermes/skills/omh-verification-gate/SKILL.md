---
name: omh-verification-gate
description: [omh] Hermes Verification Gate workflow: define and record build, lint, typecheck, test, security, docs, generated-output, and CI evidence before completion or merge. Use when the user says: verification-gate, verification gate, quality gate, release gate, test gate, build lint test, lint typecheck tests, verify before merge.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, verification]
    category: verification
    phase: verification-gate
    role: reviewer
    quality_tier: verification-gated
---

# Verification Gate

This is a Hermes-native `verification-gate` workflow skill.

## Why This Exists

`verification-gate` gives OMH a deterministic evidence surface before done/merge claims, inspired by ECC-style gates but rebuilt around OMH's prepared-versus-observed contract.

## Do Not Use When

- The user asks for visual render QA; use `visual-qa`.
- The user asks for production release readiness beyond verification commands; use `production-audit`.
- The user wants a bug-first code review of a diff; use `code-review`.

## Examples

Good example:

- Prompt: verification-gate 이 PR 머지 전에 build/lint/test/docs/CI 증거를 정리해서 PASS 가능한지 봐줘.
- Expected behavior: Prepare verification_matrix/v1, record observed_check_results/v1, and issue PASS/HOLD/BLOCK with missing evidence.
- Why: The user asks for claim verification across command and CI evidence.

Bad example:

- Prompt: verification-gate 테스트 안 돌렸지만 준비됐다고 해줘.
- Expected behavior: Return HOLD/BLOCK and list missing or stale checks instead of claiming readiness.
- Why: A verification gate is useful only if planned checks and observed results stay separate.

## Completion Checklist

- The scenario, expected behavior, observed result, and pass/fail basis are named.
- Proposed fixes are separated from observed QA evidence.
- Missing or failed verification routes back to plan, fix, or a narrower test.

## Recovery Notes

- If the expected behavior is unclear, route back to plan before running adversarial checks.
- If verification fails, return to fix or research with the failed signal instead of advancing.

## Workflow Lane

- Current lane: **Coding handoff** (`idea-to-deploy`, `cto-loop`, `deploy-and-monitor`, `code-review`, `build-failure-triage`, `verification-gate`, `security-safety-review`, `ultrawork`, `+7 more`) - coding owners, handoffs, review, CI, and merge evidence.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when Hermes must turn a change, PR, release, or claim into a concrete evidence checklist and PASS/HOLD/BLOCK verdict.

    Strong routing signals: `verification-gate`, `verification gate`, `quality gate`, `release gate`, `test gate`, `build lint test`, `lint typecheck tests`, `verify before merge`, `merge readiness gate`, `검증 게이트`, `품질 게이트`, `테스트 게이트`, `머지 전 검증`, `빌드 린트 테스트`

## Catalog Metadata

Category: `verification`
Phase: `verification-gate`
Hermes role: `reviewer`
Quality tier: `verification-gated`
Reasoning demand: `standard`

Quality bar:

- Tie every completion claim to the smallest check that proves it, then broaden for shared surfaces.
- Record command/source, freshness, exit status, and scope for each observed result.
- Return PASS only when required checks pass and stale or missing evidence is resolved.
- Keep fixes, reruns, review, CI, and merge as separate observed states.

Handoff policy:

Hermes owns the gate contract and verdict narration. Running commands, CI, browser checks, external scanners, and code fixes require observed executor, wrapper, or operator evidence.

Required inputs:

- claim or change under verification
- expected behavior and risk surface
- available local commands and CI requirements
- fresh observed outputs or explicit not-run gaps

Expected outputs:

- verification_gate_plan/v1
- verification_matrix/v1
- observed_check_results/v1 when observed
- claim_verdict/v1
- rerun_or_blocker/v1
- not-evidence boundary

Artifact expectations:

- verification_matrix/v1 covering build, lint, typecheck, unit/integration/e2e tests, generated docs, static/security checks, diff hygiene, and CI/DCO when applicable
- observed_check_results/v1 with command, timestamp/source, exit status, summary, and stale-output flag
- claim_verdict/v1 with PASS, HOLD, or BLOCK and exact missing or failed checks

Safety rules:

- Do not treat a planned command, stale output, green local check, or prepared handoff as fresh verification evidence.
- Do not collapse build, lint, tests, security, generated docs, review, CI, DCO, merge-readiness, or merge into one claim.
- Failed or unavailable checks must produce HOLD/BLOCK with a rerun or remediation path.

## Runtime Evidence

Preferred harness for this skill: `verification-gate`.

```sh
omh runtime record --skill verification-gate --harness verification-gate --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
