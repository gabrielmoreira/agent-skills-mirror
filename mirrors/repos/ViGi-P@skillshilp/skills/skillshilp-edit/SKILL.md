---
name: skillshilp-edit
description: Expert editor for improving production-quality Agent Skills. Use when reviewing, refactoring, modernizing, or maintaining existing Agent Skills while preserving their intended behaviour. Not for creating new skills.
license: MIT
metadata:
  author: Vignesh Prasad
  github: https://github.com/ViGi-P/skillshilp
  version: "2.0.0"
  purpose: meta-skill
---

# Skillshilp Edit

Improve Agent Skills as reusable software components—not as large prompts.

Your objective is to preserve intended behaviour while making Agent Skills more discoverable, composable, maintainable, deterministic, and token-efficient.

Use this skill only for **editing existing Agent Skills**. If the primary task is to create a new skill from ideas, requirements, reusable prompts, or specifications, use **skillshilp-create** instead.

If official documentation is available, treat it as the source of truth. Otherwise, follow the provided specification.

---

# Principles

| Prefer | Avoid |
|--------|-------|
| Minimal targeted changes | Unnecessary rewrites |
| Behaviour preservation | Breaking existing workflows |
| Single responsibility | God skills |
| Progressive disclosure | Bloated `SKILL.md` files |
| Modular design | Overlapping responsibilities |
| Focused references | Duplicate documentation |
| Searchable descriptions | Generic descriptions |
| Executable scripts | Large code blocks in Markdown |
| Reusable assets | Embedded templates or schemas |
| Deterministic workflows | Ambiguous instructions |
| Token efficiency | Repetition |

Preserve working behaviour unless a change is explicitly requested or clearly required to improve correctness, maintainability, or specification compliance.

---

## Preservation Rules

Unless explicitly requested, preserve:

- the skill's primary responsibility
- activation criteria
- public behaviour
- directory structure
- file names
- relative references
- documented workflows

Only introduce structural changes when they provide a clear improvement in correctness, maintainability, discoverability, or specification compliance.

---

# Workflow

## 1. Evaluate

Understand the existing Agent Skill before making changes.

Determine:

- current responsibility
- intended users
- activation criteria
- public behaviour
- requested modifications
- constraints
- dependencies
- compatibility concerns

If the requested changes significantly expand the skill's responsibility, recommend splitting it into multiple skills instead.

---

## 2. Plan

Plan the smallest set of changes required to satisfy the request.

Avoid redesigning the skill unless explicitly instructed.

When modifying the architecture:

- preserve existing behaviour where practical
- preserve activation criteria unless intentionally changing them
- preserve file organization unless a better structure provides clear value
- avoid introducing unnecessary directories or files

When a larger redesign is justified, explain why.

---

## 3. Implement

Modify only the files affected by the requested changes.

When appropriate:

- update `SKILL.md`
- update reference files
- update scripts
- update assets
- improve descriptions for discoverability
- remove duplication
- modernize outdated structures

Ensure all relative references remain valid.

---

## 4. Review

Before finalizing, verify that the updated skill is:

- specification compliant
- behaviour preserving
- discoverable
- single responsibility
- modular
- composable
- maintainable
- progressively disclosed
- minimally duplicated
- token-efficient

Validate against:

`references/constraints.md`

Review common architectural patterns:

`references/patterns.md`

Check for common design mistakes:

`references/skill-smells.md`

If any issue is found, revise before returning the updated skill.

---

# Output

Unless instructed otherwise, provide:

1. Updated directory tree (only if it changed)
2. Complete contents of every modified file
3. Valid relative file references
4. Summary of the changes made
5. Brief design notes explaining significant architectural decisions

Do not regenerate unchanged files unless explicitly requested.

---

# Final Check

Before returning the updated skill, ask:

> Does this preserve the original responsibility, activation criteria, and intended behaviour of the Agent Skill while making it easier to discover, understand, maintain, and evolve?

If any existing behaviour was intentionally changed, clearly explain why the change was necessary.

If the answer is not an unqualified **yes**, continue refining the changes.
