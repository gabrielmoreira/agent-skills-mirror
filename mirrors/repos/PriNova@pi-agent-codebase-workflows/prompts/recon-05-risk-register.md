---
description: "Structured recon pass 5 risk register"
argument-hint: "[focus]"
---
Before writing/updating structured artifacts, after loading the selected skill, load shared refs relative to that skill: `../_shared/references/artifact-api.md`, `../_shared/references/schemas/common.schema.json`, and only the matching artifact schema(s). Follow the skill Structured Artifact Write/Update Protocol for scope resolution, stable IDs, upserts, evidence, reference integrity, status transitions, deterministic YAML formatting, and validation. Resolve `<docs-root>` exactly per the selected skill: canonicalize `workspace_root`, use repo-local `<workspace_root>/docs/agent/api` only when that skill says repo-local applies and the directory exists, otherwise strip one leading slash/backslash from `workspace_root`, replace every slash, backslash, and colon with `-`, wrap with `--`, and use `~/.pi/agent/workspaces/<workspace-fingerprint>/docs/agent/api`. Use `/skill:codebase-recon` Pass 5. Read structured architecture/data/invariants/dependency YAML.

Write/update `risk-register.yaml`.

Each risk should include at least:
- failure mode/title
- affected refs
- severity/confidence
- recommended action
- evidence refs

Prefer quality, security, reliability, and operability risks that are clearly evidenced by the repo over generic speculation. YAML only. Focus: $ARGUMENTS.
