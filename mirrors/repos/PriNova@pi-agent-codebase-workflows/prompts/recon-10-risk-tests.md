---
description: "Structured recon pass 10 risk-to-tests"
argument-hint: "[focus]"
---
Before writing/updating structured artifacts, after loading the selected skill, load shared refs relative to that skill: `../_shared/references/artifact-api.md`, `../_shared/references/schemas/common.schema.json`, and only the matching artifact schema(s). Follow the skill Structured Artifact Write/Update Protocol for scope resolution, stable IDs, upserts, evidence, reference integrity, status transitions, deterministic YAML formatting, and validation. Resolve `<docs-root>` exactly per the selected skill: canonicalize `workspace_root`, use repo-local `<workspace_root>/docs/agent/api` only when that skill says repo-local applies and the directory exists, otherwise strip one leading slash/backslash from `workspace_root`, replace every slash, backslash, and colon with `-`, wrap with `--`, and use `~/.pi/agent/workspaces/<workspace-fingerprint>/docs/agent/api`. Use `/skill:codebase-recon` Pass 10.

Write/update `testing-strategy.yaml` with:
- `test_structure`
- `quality_attribute_coverage`
- `coverage_gaps`
- `risk_to_test_priorities`
- `known_blockers`
- `operability_checks` when relevant

Connect important risks and quality attributes to concrete validation expectations. YAML only. Focus: $ARGUMENTS.
