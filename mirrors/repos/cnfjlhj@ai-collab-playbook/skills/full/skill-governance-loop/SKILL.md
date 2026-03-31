---
name: skill-governance-loop
description: Use when the user asks to "review this skill", "analyze skill quality", "skill version update", "整理 skills", "skill governance", or wants a repeatable keep/disable/archive loop built from real skill failures instead of abstract best practices.
version: 0.1.0
user-invocable: true
---

# Skill Governance Loop

Use this skill to govern skills by evidence, not taste.

Start from a real case, a concrete version update, or a local inventory problem.
Do not begin with abstract "best practices" unless they are anchored to an observed failure mode.

## When to Use

- The user says `skill version update`, `review this skill`, `analyze skill quality`, `整理 skills`, `skill governance`, `keep or disable these skills`, or similar.
- A skill triggers poorly, feels bloated, overlaps with another skill, or is suspected to belong in `AGENTS.md` instead.
- The user wants a repeatable loop for future skill iteration instead of one-off edits.

## Core Rule

Every governance pass must produce three outputs:

1. a concrete `case`
2. a scored `audit`
3. a `decision`

Without all three, the loop is incomplete.

## Workflow

1. If the task is inventory-wide, run `skills-governance` first to get a filesystem-backed baseline.
2. Create a case folder with `python3 scripts/init_case.py --skill <name> --reason <slug>`.
3. Fill `case.md` with the real symptom, expected behavior, observed behavior, and evidence.
4. Run `python3 scripts/static_audit.py <skill-path>` to get a baseline scorecard.
5. If the decision matters, compare real prompts or run a trigger eval using local eval tooling such as `skill-creator-plus`.
6. Decide one of: `keep-enabled`, `keep-disabled`, `merge`, `split`, `archive`, `move-to-agents`, `move-to-skill`.
7. If the skill changes, bump the version and record the hypothesis for the next iteration.

## Read Next

- Read `references/workflow.md` for the full loop.
- Read `references/rubric.md` for scoring dimensions.
- Read `references/agents-vs-skill.md` before moving content between `AGENTS.md` and a skill.

## Output Contract

Report at least:

- the concrete case being solved
- the target skill or skill set
- the static audit result
- any empirical eval evidence used
- the final decision and why
- the next version hypothesis

## Acceptance

A good run:

- starts from a concrete failure, overlap, or version-change request
- does not confuse static quality with proven usefulness
- separates `always-on rules` from `task-specific workflows`
- leaves behind reusable artifacts for the next iteration
