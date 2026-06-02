# Security Review Discipline

Use this reference when `controlflow-review` or `controlflow-plan-audit` enters a security-focused review pass.

## Confidence Threshold

- **Flag an issue as a security vulnerability only when confidence is > 80%.**
- Below that threshold: record as an observation or suggested follow-up, not as a blocking finding.

This avoids review noise and keeps the signal of "this is a real vulnerability" meaningful.

## Explicit Exclusion List

Do NOT flag the following categories during a security review pass — they belong to other review modes or are out of scope:

- Denial-of-service (DoS) without a concrete exploitation chain
- Secrets-on-disk (a separate hygiene concern)
- Rate-limiting gaps without a concrete abuse scenario
- Theoretical issues with no realistic exploitation path
- Style or formatting issues

## What to Focus On

A security review should prioritise issues with a clear exploitation path against:

- **Authentication & session handling** — token validation, expiry, replay, fixation.
- **Authorization** — IDOR, missing scope checks, privilege escalation paths.
- **Input handling** — injection (SQL, command, template, header, log), unsafe deserialisation, path traversal, SSRF.
- **Secrets in code** — credentials, tokens, or keys hard-coded in source or test fixtures.
- **Untrusted data crossing trust boundaries** — sanitisation, validation, encoding at the right layer.
- **Cryptographic misuse** — weak primitives, missing IV/nonce, hard-coded keys, insecure randomness.
- **Dependency risks** — known-vulnerable packages directly involved in the changed code paths.

## Output Shape for Findings

Each security finding should include:

- **Severity** — `critical` / `high` / `medium` / `low`.
- **Confidence** — explicit number or descriptor; below 80% means downgrade to observation.
- **File and line** — concrete evidence.
- **Exploitation path** — one or two sentences explaining how an attacker reaches the issue.
- **Suggested fix** — concrete remediation, not generic advice.

## When to Use This Skill vs. General Review

| Situation | Use |
| --- | --- |
| User asks for a security review specifically | This reference + `controlflow-review` |
| Plan touches authentication, authorization, secrets, or trust boundaries | This reference during `controlflow-plan-audit` |
| General code review with security only as one dimension | Apply the threshold and exclusion list, but do not gate the whole review on it |
| Ordinary refactor with no trust-boundary impact | Skip this reference |
