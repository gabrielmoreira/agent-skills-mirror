---
description: Review current diff against architecture and invariants
argument-hint: "[scope]"
---
Use `/skill:arch-code-review`.

Review target/scope, if provided:
$ARGUMENTS

Use scope to focus review on a module/package/app/service/path when diff spans multiple areas. Use `docs/agent/SCOPES.md` if present to discover matching scoped docs and cross-scope contracts.

Review current diff. Do not edit code. Provide verdict, findings with severity/evidence/fix direction, missing tests, docs updates, drift risk, final recommendation.
