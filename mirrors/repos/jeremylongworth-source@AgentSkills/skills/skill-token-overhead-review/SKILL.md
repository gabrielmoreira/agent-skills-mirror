---
name: skill-token-overhead-review
description: Review the context, token, tool, and process overhead added by agent skills. Use when Codex is asked whether a skill is too verbose, too broad, costly to invoke, duplicative, or worth its context/tool overhead.
license: MIT
---

# Skill Token Overhead Review

## Core Workflow

1. Identify the skill or bundle, trigger path, host, loaded files,
   tools/scripts used, repeated-run pattern, and target artifact.
2. Estimate overhead from added metadata, instructions, references, tool calls,
   turns, command output, MCP tools, or setup steps. Use exact token counts only
   when measured.
3. Compare overhead against output improvement from scenario or before/after
   evidence.
4. Flag broad triggers, duplicate guidance, stale references, unnecessary
   scripts, oversized command output, and host-specific setup leakage.
5. Recommend keep, trim, split, merge, lazy-load, compose through a skillset or
   orchestrator, move to references/scripts, isolate in a host adapter, or defer.
6. Preserve essential safety and validation instructions even when trimming.

## Measurement Protocol

- Capture baseline and skill-enabled runs with the same prompt and source
  material when practical.
- Record activated skills, referenced files, scripts/commands, MCP servers or
  tools, output size, turns, and validation results.
- For repeated workflows, check whether raw research, tool output, or reasoning
  compounds across items or runs.
- Treat host-specific features separately. For example, Claude Code
  `context: fork`, `!command`, and MCP Tool Search can reduce main-context load,
  but they are adapter behaviors rather than portable skill requirements.
- Do not count shell injection as free context: inserted command output still
  becomes prompt content.

## Safety Rules

- Do not remove safety, approval, freshness, or validation guidance only to save
  context.
- Do not optimize for token count when the task is high-risk and needs review
  boundaries.
- Do not claim exact token savings unless measured.
- Do not add host-specific optimization fields to portable skills without a
  compatibility note or adapter boundary.

## Deliverable Shape

For overhead reviews, provide:

- Skill or bundle reviewed
- Loaded context and tools
- Overhead estimate
- Measurement method and limits
- Output value observed
- Duplicative or stale guidance
- Trim/split/merge/compose recommendations
- Host adapter recommendations
- Safety instructions to preserve

## References

- Read `references/skill-token-overhead-review-checklist.md` when reviewing
  context or tool overhead.
