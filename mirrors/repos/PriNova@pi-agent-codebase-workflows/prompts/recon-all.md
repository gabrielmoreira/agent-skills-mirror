---
description: "Structured codebase reconstruction all passes"
argument-hint: "[focus]"
---
Before writing/updating structured artifacts, after loading the selected skill, load shared refs relative to that skill: `../_shared/references/artifact-api.md`, `../_shared/references/schemas/common.schema.json`, and only the matching artifact schema(s). Follow the skill Structured Artifact Write/Update Protocol for scope resolution, stable IDs, upserts, evidence, reference integrity, status transitions, deterministic YAML formatting, and validation. Resolve `<docs-root>` exactly per the selected skill: canonicalize `workspace_root`, use repo-local `<workspace_root>/docs/agent/api` only when that skill says repo-local applies and the directory exists, otherwise strip one leading slash/backslash from `workspace_root`, replace every slash, backslash, and colon with `-`, wrap with `--`, and use `~/.pi/agent/workspaces/<workspace-fingerprint>/docs/agent/api`. Use `/skill:codebase-recon` all-in-one mode. Produce canonical YAML artifacts under the resolved structured docs root; root `AGENTS.md` may be generated in Pass 6 for harness interoperability. No other Markdown docs.

Reconstruct not only inventory and structure, but also:
- project intent and likely quality attributes when inferable
- trust boundaries, sensitive data, retention/compliance notes
- architecture rationale/tradeoffs when evidence exists
- reliability, observability, and security expectations from code/config/docs
- risks, recommended actions, and test/operability coverage

If repo is too large, finish current pass and recommend next pass. Focus: $ARGUMENTS.
