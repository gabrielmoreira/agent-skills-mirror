---
name: skill-token-overhead-review
description: Review the context, token, tool, and process overhead added by agent skills. Use when Codex is asked whether a skill is too verbose, too broad, costly to invoke, duplicative, or worth its context/tool overhead.
license: MIT
---

# Skill Token Overhead Review

## Core Workflow

1. Identify the skill or bundle, trigger path, loaded files, tools/scripts used,
   and target artifact.
2. Estimate overhead from added instructions, references, tool calls, turns, or
   setup steps. Use exact token counts only when available.
3. Compare overhead against output improvement from scenario or before/after
   evidence.
4. Flag broad triggers, duplicate guidance, stale references, unnecessary
   scripts, and host-specific setup leakage.
5. Recommend keep, trim, split, merge, lazy-load, or defer.
6. Preserve essential safety and validation instructions even when trimming.

## Safety Rules

- Do not remove safety, approval, freshness, or validation guidance only to save
  context.
- Do not optimize for token count when the task is high-risk and needs review
  boundaries.
- Do not claim exact token savings unless measured.

## Deliverable Shape

For overhead reviews, provide:

- Skill or bundle reviewed
- Loaded context and tools
- Overhead estimate
- Output value observed
- Duplicative or stale guidance
- Trim/split/merge recommendations
- Safety instructions to preserve

## References

- Read `references/skill-token-overhead-review-checklist.md` when reviewing
  context or tool overhead.
