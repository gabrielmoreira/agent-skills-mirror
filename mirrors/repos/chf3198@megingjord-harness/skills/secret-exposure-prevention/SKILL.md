---
name: secret-exposure-prevention
description: Prevent secret leakage across git history, package artifacts, logs, and docs. Use when editing workflows, packaging configuration, environment files, or release automation.
---

# Secret Exposure Prevention

## When to use

- On changes involving `.env`, publish scripts, workflow files, and package include/exclude rules.
- Before packaging/publishing distributable artifacts.
- After any secret-handling incident or near-miss.

## Procedure

1. Identify secret-bearing file patterns in repo and tooling context.
2. Verify packaging exclude rules (`.vscodeignore`, `.npmignore`, artifact manifests).
3. Verify prevention controls (pre-commit scanning, CI scanning, secret scanning backstops).
4. Validate that examples and docs use placeholders, never live tokens.
5. Propose targeted guardrails with minimal operational overhead.

## Output format

- `risk_status`: low|medium|high
- `exposure_surfaces`: git|artifact|logs|docs
- `missing_controls`: specific missing guardrails
- `recommended_controls`: prevention-first controls in priority order
- `evidence`: files, workflows, and policies reviewed

## Standards

- Prevention first, detection second.
- Never accept shipping secret-bearing files in distributable artifacts.
- Keep false-positive handling explicit and auditable.
