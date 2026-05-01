---
name: repo-onboarding-standards
description: Onboard any repository into a standardized Copilot + CI governance baseline. Use for new repos and first-time sessions to ensure immediate standards adoption.
---

# Repo Onboarding Standards

## When to use

- First session in a new repository.
- Existing repositories lacking standardized AI customization and release/security gates.
- Requests like: "include all global-skills in your initialization process."

## Procedure

1. Run `global-skills-bootstrap` in `mode=init` for repository scaffolding.
2. Classify repository type and risk profile using existing routing skills.
3. Generate baseline repo instructions (`.github/copilot-instructions.md`) with build/test/gate truth.
4. Add targeted `.github/instructions/*.instructions.md` files for stack-specific rules.
5. Verify CI has minimum baseline: lint/test, dependency/security review, artifact/release checks.
6. Add or update release policy controls (version integrity, docs sync, packaging audit).
7. For platforms that support exact-version install/pin, require version-selectability controls:
	- immutable artifact retention,
	- exact-version install smoke checks,
	- canonical version index/source alignment for update prompts,
	- documented rollback and version-yank policy.
8. Produce an onboarding report with required vs optional controls and evidence.

## Required handoffs

- Run `global-skills-bootstrap` first for new repositories.
- Route standards selection via `repo-standards-router`.
- Route GitHub workflow governance controls via `github-ops-tree-router`.
- Use `workflow-self-anneal` only post-failure/process mismatch.

## Output format

- `repo_classification`: type + confidence
- `baseline_status`: complete|partial|missing
- `required_controls`: must-have controls
- `optional_controls`: nice-to-have controls
- `execution_plan`: sequenced rollout tasks
- `evidence`: files and checks used for conclusions

## Standards

- Prefer smallest correct baseline over over-engineered policy stacks.
- Require objective verification gates for each recommended control.
- Do not claim onboarding complete without evidence for every required control.
- Do not mark release governance complete when an app type can support exact-version installability but lacks enforceable controls for it.
