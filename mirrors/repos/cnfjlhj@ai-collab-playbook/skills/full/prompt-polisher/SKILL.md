---
name: prompt-polisher
description: "Use when the user explicitly wants rough notes, voice transcription, or stream-of-consciousness instructions rewritten into a clean reusable prompt for another model or for later execution. Do not use this just because the input is messy; use input-triage when the job is to separate goals, claims, and options."
---

# Prompt Polisher

## Overview

This skill turns rough instruction material into a prompt artifact. It is for prompt rewriting, not for general requirement discovery or mixed-signal task triage.

Use it when the user wants a better prompt as the output. If the real need is to understand a messy request before acting, route to the more general triage skill first.

## Rules

- Trigger only when the user explicitly wants prompt polishing, prompt cleanup, or prompt preparation.
- Preserve the user's real task, constraints, and tone instead of inflating the prompt.
- Ask only the minimum clarification needed if a missing detail would materially weaken the rewritten prompt.
- Preview the polished prompt before execution unless the user clearly wants rewrite-and-run in one motion.
- Keep the output reusable and concise; do not add model-specific padding unless the target model matters.
- If the input is already clear enough to execute directly, say so instead of forcing a rewrite.

## When to Use

Use when:

- the user says "polish this," "clean this up," or "turn this into a prompt"
- rough notes or voice-style text should become a reusable prompt artifact
- the user wants the same instructions packaged for Claude, Codex, or another model
- the main deliverable is the improved prompt itself

Do not use when:

- the user wants the task executed directly rather than rewritten as a prompt
- the job is to sort goals, observations, claims, and proposed fixes
- brainstorming or planning is still needed before a prompt can be meaningfully written
- the input is already clear enough and no prompt artifact is needed

## References

- Guidance: `reference.md`
- Examples: `examples.md`

## Output Pattern

- cleaned source intent
- polished prompt
- optional short note on what changed or what still needs clarification
