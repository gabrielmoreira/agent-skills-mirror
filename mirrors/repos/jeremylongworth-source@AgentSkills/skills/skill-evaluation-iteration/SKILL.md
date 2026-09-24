---
name: skill-evaluation-iteration
description: Evaluate, forward-test, and improve Codex skills. Use when Codex is asked to test a skill, compare performance with and without a skill, improve a skillset, make skills stronger, validate skill usefulness, create acceptance tests for skills, or iterate skill instructions based on realistic scenarios.
license: MIT
---

# Skill Evaluation Iteration

## Core Workflow

1. Define the target behavior and realistic user scenarios before editing the skill.
2. Run or simulate a baseline without the skill when practical.
3. Run or simulate the same scenario with the skill.
4. Compare outputs by decision quality, missing steps, correctness, concision, safety, tool use, validation, and deliverable usefulness.
5. Patch the skill to close observed gaps. Keep changes small and domain-specific.
6. Validate the skill folder with the official validator.
7. Repeat only when the new test reveals a material gap.

For model-specific evaluations, record the exact model, reasoning setting,
host, active instructions, available tools, and source inputs. Hold those
constant when comparing skill versions. Label source reviews and simulations
separately from live runs; only claim improvements supported by recorded
outputs. Include a negative case for unnecessary questions or skill use.

## Output Contract

For skillset improvement work, return:

- Scenarios evaluated
- Rubric used
- Gaps found
- Skills changed
- Validation run
- Remaining risks or deferred improvements

## Patch Decision Rule

Patch a skill only when the test reveals a concrete trigger, workflow, output, validation, freshness, or routing gap. Do not edit skills just to make them longer.

## Evaluation Criteria

- Trigger accuracy: skill activates for the right requests and avoids unrelated ones.
- Metadata sync: `agents/openai.yaml` still reflects the current `SKILL.md` purpose, especially after major edits.
- Scope and discovery: the skill is installed in the narrowest useful scope with a precise description; global instructions do not accumulate skill-routing lists.
- Context efficiency: SKILL.md is concise and references are loaded only when needed.
- Procedural value: skill changes the agent's workflow, not just wording.
- Quality bar: output includes acceptance criteria, validation, and domain-specific checks.
- Robustness: skill handles edge cases, constraints, and missing context.
- Maintainability: skill avoids stale facts unless it includes a freshness rule.
- Hygiene: generated scaffold placeholders, TODOs, stale examples, and irrelevant boilerplate are removed.

## When To Forward-Test

Forward-test when the skill is complex, high-impact, or repeatedly used. Use realistic prompts and raw artifacts. Avoid leaking expected answers into the test prompt.

## References

- Read `references/skill-evaluation-checklist.md` when evaluating or improving a skill.
- Read `references/skill-evaluation-scenarios.md` when selecting reusable scenarios for a broader skillset evaluation pass.
