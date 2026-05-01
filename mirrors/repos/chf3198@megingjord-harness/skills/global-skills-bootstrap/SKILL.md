---
name: global-skills-bootstrap
description: Initialize a repository so global skills are always loaded first through repository instructions, local hooks, and governance presence checks.
argument-hint: [repo-path: /absolute/path] [mode: init|audit] [profile: strict|standard]
user-invocable: true
disable-model-invocation: false
---

# Global Skills Bootstrap

## Purpose

Create a repeatable initialization flow so a new project can be onboarded with one request and consistently route through global governance skills.

## Trigger phrase

If the user asks to "include all global-skills in your initialization process", run this skill in `mode=init`.

Preferred command:
- `global-skills-bootstrap-repo /absolute/path/to/repo init`
- `global-skills-bootstrap-repo /absolute/path/to/repo audit`

## What this skill installs

1. Repository-global instruction file at `.github/instructions/global-skills.instructions.md`.
2. Local governance check script at `.github/scripts/check-global-governance.sh`.
3. Optional Git hooks at `.githooks/pre-commit` and `.githooks/pre-push`.
4. CI workflow gate at `.github/workflows/global-governance-presence.yml`.
5. OpenClaw overlay at `.github/instructions/openclaw-universal.instructions.md`.
6. Local git `core.hooksPath` set to `.githooks` when the repo is a git repository.

## Required routing contract

The generated instruction file must require this order:

1. `repo-standards-router`
2. `network-platform-resources` when task may benefit from remote execution or offloading
3. `openrouter-free-failover` when configuring or troubleshooting OpenClaw/OpenRouter models
4. `web-regression-governance` when repo type is `website-static` or `web-app`
5. `github-ops-tree-router` for rulesets/required checks/governance controls
6. `workflow-self-anneal` only after failures/process drift
7. `llm-wiki-ops` when querying compiled knowledge from `~/.copilot/wiki/`

## Hard constraints

- Do not overwrite existing files without preserving user content.
- Additive changes only unless user explicitly requests replacement.
- CI gate must fail if required global-governance files are missing.
- Hooks are advisory acceleration; server-side CI/ruleset checks remain authoritative.
- Prefer one canonical bootstrap path over multiple parallel installers to reduce drift and missed skills.

## Output format

```text
GLOBAL_SKILLS_BOOTSTRAP_REPORT
repo_path: <absolute path>
mode: <init|audit>
profile: <strict|standard>
created_files:
- <list>
updated_files:
- <list>
hook_status:
- pre_commit: <installed|missing>
- pre_push: <installed|missing>
ci_presence_gate: <installed|missing>
routing_contract: <present|missing>
decision:
- <apply|defer|NO_CHANGE>
next_steps:
- <ordered actionable steps>
```
