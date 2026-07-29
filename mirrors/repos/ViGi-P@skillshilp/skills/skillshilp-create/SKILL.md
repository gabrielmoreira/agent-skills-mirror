---
name: skillshilp-create
description: Expert architect for creating new production-quality Agent Skills. Use when designing new skills, converting reusable prompts into skills, or architecting modular skill collections. Not for modifying existing skills.
license: MIT
metadata:
  author: Vignesh Prasad
  github: https://github.com/ViGi-P/skillshilp
  version: "2.0.0"
  purpose: meta-skill
---

# Skillshilp Create

Design Agent Skills as reusable software components—not as large prompts.

Your objective is to produce Agent Skills that are discoverable, composable, maintainable, deterministic, and token-efficient.

Use this skill only for **creating new skills**. If the primary task is to modify, refactor, review, or improve an existing skill, use **skillshilp-edit** instead.

If official documentation is available, treat it as the source of truth. Otherwise, follow the provided specification.

---

# Principles

| Prefer | Avoid |
|--------|-------|
| Single responsibility | God skills |
| Progressive disclosure | Bloated `SKILL.md` files |
| Modular design | Overlapping responsibilities |
| Focused references | Duplicate documentation |
| Searchable descriptions | Generic descriptions |
| Executable scripts | Large code blocks in Markdown |
| Reusable assets | Embedded templates or schemas |
| Deterministic workflows | Ambiguous instructions |
| Token efficiency | Repetition |

Every file should have a clear purpose. Avoid introducing directories, files, or abstractions that do not meaningfully improve maintainability or reuse.

---

# Workflow

## 1. Evaluate

Determine whether the request should become an Agent Skill.

An Agent Skill should represent a reusable capability that another agent can reliably discover and invoke.

If the request is better solved by a script, template, document, workflow, or one-off prompt, recommend that instead.

Define:

- responsibility
- intended users
- activation criteria
- inputs
- outputs
- constraints
- dependencies
- edge cases

If multiple unrelated capabilities are identified, split them into separate skills with clearly defined responsibilities.

---

## 2. Design

Design the architecture before writing any files.

Create only the directories that add value.

Typical layout:

```text
skill-name/
├── SKILL.md
├── README.md          # optional
├── references/
├── scripts/
└── assets/
```

Decide where each piece of information belongs.

### `SKILL.md`

Keep concise.

Include only:

- activation criteria
- workflow
- critical rules
- validation
- references to supporting files

### `references/`

Store information intended to be read by the model, such as:

- technical documentation
- APIs
- algorithms
- schemas
- workflows
- FAQs
- design guidance

### `scripts/`

Store executable logic.

Scripts should validate inputs, document dependencies, fail predictably, and avoid embedding large prompts where executable code is more appropriate.

### `assets/`

Store reusable resources, such as:

- templates
- configuration files
- diagrams
- sample data
- example documents

---

## 3. Implement

Generate:

- directory tree
- valid frontmatter
- concise `SKILL.md`
- supporting reference files
- scripts when appropriate
- assets when appropriate

Descriptions should clearly explain:

- what the skill does
- when another agent should activate it
- what makes it distinct from similar skills

Assume the description will be used for automatic discovery.

---

## 4. Validate

Before finalizing, verify that the skill is:

- specification compliant
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

If any issue is found, revise the design before returning the skill.

---

# Output

Unless instructed otherwise, provide:

1. Complete directory tree
2. Complete contents of every generated file
3. Valid relative file references
4. Brief design notes explaining important architectural decisions

Do not omit files for brevity unless explicitly requested.

---

# Final Check

Before returning the skill, ask:

> If this skill were published in a large public registry, would another agent reliably discover it, understand when to activate it, compose it with other skills, and successfully execute it without additional explanation?

If the answer is not an unqualified **yes**, continue refining the design.
