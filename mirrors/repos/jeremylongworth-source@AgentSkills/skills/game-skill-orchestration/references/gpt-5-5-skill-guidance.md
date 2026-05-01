# GPT-5.5 Skill Guidance

Use this reference when updating game-development skills or designing prompts/workflows for a GPT-5.5-class model.

## Current Official Guidance Snapshot

As of April 29, 2026, official OpenAI developer docs identify `gpt-5.5` as the flagship model for complex reasoning and coding. The docs recommend treating GPT-5.5 as a model family to tune for, not as a drop-in replacement for earlier GPT-5.x prompts.

Verify current model status from official OpenAI docs when the user asks for latest availability, pricing, context windows, model IDs, endpoint support, or migration guidance.

## Prompt And Skill Implications

- Start with the product outcome and success criteria.
- Remove unnecessary procedural scaffolding unless the workflow must happen in a fixed order.
- Define allowed side effects and stopping rules for agentic tasks.
- Put stable reusable skill guidance before dynamic project context when designing prompts for caching.
- Keep output contracts explicit, but prefer API structured outputs for strict machine-readable schemas.
- Tune `reasoning.effort` empirically. `medium` is the balanced default; use `low` for efficient bounded work and `high` or `xhigh` for difficult planning, architecture, or review tasks.
- Use `text.verbosity` or explicit word/section budgets to control final answer length separately from reasoning quality.
- Put tool-specific behavior in tool descriptions when possible. Keep skill instructions focused on domain judgment, routing, quality bars, and validation.

## Skill Quality Bar

A strong skill should include:

- A precise trigger description in frontmatter.
- A short core workflow.
- Domain-specific decision criteria.
- A deliverable shape or output contract.
- A validation or review checklist, preferably in `references/`.
- Clear guidance on when to load references.
- Minimal duplicated boilerplate across skills.

## Anti-Patterns To Remove

- Long generic explanations that a modern model already knows.
- Rigid step-by-step process where several paths are valid.
- Hidden assumptions about engine, platform, audience, or scope.
- Domain advice without acceptance criteria or validation.
- Large all-in-one skills that should be decomposed into focused skills.
- Stale model IDs, pricing, or API availability embedded as permanent facts without a verification instruction.
