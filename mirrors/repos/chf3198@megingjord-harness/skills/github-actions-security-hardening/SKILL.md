---
name: github-actions-security-hardening
description: Enforce secure GitHub Actions posture with least-privilege tokens, pinned dependencies, runner risk controls, and workflow supply-chain checks.
argument-hint: "[mode: audit|plan|remediate|verify] [scope: repo|org] [runner: hosted|self-hosted|mixed] [policy-profile: strict|standard|light]"
user-invocable: true
disable-model-invocation: false
---

# GitHub Actions Security Hardening

## Purpose

Reduce CI/CD and workflow supply-chain risk while preserving delivery velocity.

## Core controls

1. `GITHUB_TOKEN` least privilege (default read, elevate per-job only when required).
2. Third-party actions pinned to full commit SHA where policy requires.
3. Secrets hygiene (least privilege, rotation, masking, no plaintext leakage).
4. OIDC preferred over long-lived cloud credentials.
5. CODEOWNERS coverage for `.github/workflows/`.
6. Dependency and vulnerability monitoring for Actions dependencies.
7. Runner strategy hardening (hosted preferred for untrusted PRs; strict controls for self-hosted).
8. Optional: block or limit Actions ability to create/approve PRs where policy requires.

## Hard constraints

- No auto-remediation that broadens permissions.
- No direct write changes to production deployment workflows without explicit approval trail.
- If workflow trust boundaries are unclear, return `NO_CHANGE`.

## Output contract

```text
ACTIONS_SECURITY_REPORT
mode: <audit|plan|remediate|verify>
scope: <repo|org>
runner: <hosted|self-hosted|mixed>
policy_profile: <strict|standard|light>

checks:
- id: A1
  control: <token-permissions|pinning|oidc|...>
  result: <pass|fail|partial>
  evidence: <file/setting/observation>
  risk: <low|medium|high>

actions:
1) priority: <P1|P2|P3>
   change: <specific remediation>
   verification: <objective check>

decision:
- <apply|defer|NO_CHANGE>

missing_evidence:
- <none or required artifacts>
```

## Invocation policy

Run in pre-merge for workflow/security-sensitive changes and in periodic governance audits.

## Repo workflow inventory

| Workflow | Trigger | Permissions | Status |
|---|---|---|---|
| `.github/workflows/lint.yml` | PR/push to main | default read | ✅ active |
| `.github/workflows/label-lint.yml` | issues events | `issues:write`, `contents:read` | ✅ active (ADR-010) |

`label-lint.yml` enforces ADR-010 rules 1–4 on every issue event. Any violation
posts an explanatory comment and fails the check. See
`research/adr/010-ticket-status-role-model.md`.
