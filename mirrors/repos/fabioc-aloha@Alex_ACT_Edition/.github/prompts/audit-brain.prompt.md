---
description: "Run a local ACT Edition brain audit via the brain-auditor worker and return severity-ranked fixes"
mode: agent
agent: brain-auditor
lastReviewed: 2026-05-13
---

# Audit Brain

Run a local brain audit for this repository and produce a concise, actionable report.

## Steps

1. Use local deterministic checks available from repository contents:
	- frontmatter completeness and freshness
	- manifest and artifact consistency
	- cross-reference integrity across instructions, skills, prompts, and agents

2. Validate findings in files and classify by severity (`high`, `medium`, `low`).

3. Report findings first with:

- file path
- why it matters
- minimal fix

4. If user approves, apply fixes and rerun the same local checks.

## Guardrails

- Do not require external API keys to complete the local audit.
- Do not claim a file is broken without file-level evidence.
- Keep changes minimal and reversible.
