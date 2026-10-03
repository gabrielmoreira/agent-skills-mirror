---
title: Security boundaries
applicability:
- When the outcome depends on what may cross a trust boundary or who may act across it
---

Identify the asset, actors, trust boundary, allowed action, and concrete path from input to effect. Keep authentication, authorization, validation, escaping, and auditability distinct; success at one does not imply another.

Validate at the boundary that owns the contract, preserve structured values until the final sink, and use parameterized or platform-provided mechanisms for interpreters, queries, paths, templates, and protocols. Grant the least capability the operation needs and make denial the safe default.

Verify both permitted and denied paths, including confused-deputy, cross-tenant, replay, partial-failure, and disclosure cases that the reachable design admits. Use sanitized fixtures. Do not place secrets or harmful material in tests, logs, examples, reports, or delegated briefs.

A live security probe, credential use, privilege change, external scan, or disclosure needs explicit authority beyond permission to edit code.
