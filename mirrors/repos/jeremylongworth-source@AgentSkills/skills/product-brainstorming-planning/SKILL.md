---
name: product-brainstorming-planning
description: Explore intent and shape ideas before implementation planning. Use when Codex is asked to brainstorm, ideate, plan a feature/product/workflow, clarify a vague idea, compare approaches, discover requirements, create a PRD, define MVP scope, or turn rough goals into an implementation-ready brief.
license: MIT
---

# Product Brainstorming Planning

## Core Workflow

1. Separate brainstorming from implementation planning. First clarify what should exist and why; only then decide how to build it.
2. Identify user, problem, motivation, desired outcome, constraints, risks, non-goals, and decision criteria.
3. Use supplied context and repository evidence first. Ask only questions whose answers materially change scope, correctness, or the chosen approach; do not require a fixed number of questions.
4. Explore multiple approaches, including a small MVP, a strong version, and a risky/ambitious version.
5. Surface decisions that need the user's choice. State reasonable assumptions for routine gaps and continue work that does not depend on the answer.
6. Convert the selected direction into a build-ready brief with acceptance criteria.

## Handoff Rule

For planning-only requests, finish with the brief and a clear next-skill
recommendation. When the user also requested implementation and the direction
is sufficiently specified, continue into the relevant workflow within the same
task. A skill handoff is not a new approval gate. Preserve explicit planning
boundaries and any required repository review. Examples:

- Game concepts: hand off to `game-skill-orchestration`.
- Growth, sales, or marketing ideas: hand off to `growth-strategy-orchestration`.
- React/Next performance ideas: hand off to `react-next-performance-optimization`.
- UI critique or visual polish: hand off to `visual-ui-ux-audit`.
- Skill improvement ideas: hand off to `skill-evaluation-iteration`.

## Brainstorming Modes

- Discovery: clarify the problem, audience, and success criteria.
- Divergence: generate several viable directions.
- Convergence: compare options and choose a path.
- Design shaping: define workflows, states, edge cases, and data.
- Implementation readiness: translate the idea into scope, milestones, and validation.

## Output Contract

- Intent summary
- Assumptions and unknowns
- User/job/story
- Options with tradeoffs
- Recommended direction
- MVP and later versions
- Acceptance criteria
- Open questions that materially change scope

## References

- Read `references/brainstorming-planning-checklist.md` when shaping a broad or ambiguous idea.
