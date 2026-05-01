---
name: secrets-handling-review
description: Review how agent skills handle secrets and credentials. Use when Codex is asked to inspect skills, scripts, examples, logs, templates, or MCP/tool instructions for secret access, redaction, storage, exposure, or approval requirements.
license: MIT
---

# Secrets Handling Review

## Core Workflow

1. Identify any credentials, tokens, keys, cookies, env vars, config files, or
   secret-like placeholders mentioned by the skill.
2. Check whether the skill asks to read, print, store, transmit, log, or commit
   secrets.
3. Review scripts and examples for accidental secret exposure in output,
   screenshots, generated files, traces, or error reports.
4. Verify redaction, least privilege, and explicit approval expectations.
5. Recommend removal, placeholder replacement, redaction rules, `.gitignore`
   updates, or blocked publication.
6. Report residual risk and safe-use instructions.

## Safety Rules

- Do not reveal secret values in review output.
- Do not commit secrets or secret-like sample values.
- Do not approve a skill that asks for broad credential access unrelated to the
  task.
- Prefer placeholders and user-managed environment setup over embedded secrets.

## Deliverable Shape

For secrets reviews, provide:

- Secret-like inputs found
- Exposure paths
- Redaction and storage gaps
- Required changes
- Safe handling instructions
- Pass/warn/fail/block recommendation

## References

- Read `references/secrets-handling-review-checklist.md` when reviewing skills,
  scripts, examples, logs, templates, or generated files for secrets risk.
