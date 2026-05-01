# Skills Library

## Purpose

Reusable domain-specific patterns and best practices for agent consumption. Planner selects relevant skills during planning and includes them as `skill_references` in plan phases. Implementation agents read referenced skills before starting work.

## Directory Structure

```
skills/
├── README.md          # This file — overview and discovery protocol
├── index.md           # Master index mapping domains to skill files
└── patterns/          # Domain-specific pattern files
    ├── tdd-patterns.md
    ├── error-handling-patterns.md
    ├── security-patterns.md
    ├── performance-patterns.md
    ├── completeness-traceability.md
    ├── integration-validator.md
    └── idea-to-prompt.md
```

## Format Specification

Each pattern file follows this structure:

- **Title** — Domain name
- **Applicability** — When to use this skill
- **Patterns** — Numbered list of best practices (concise, actionable)
- **Anti-Patterns** — Common mistakes to avoid
- **References** — Links to authoritative sources

**Constraint:** Each pattern file must be ≤100 lines to fit within agent context budgets.

## Discovery Protocol

1. Planner reads `skills/index.md` during planning
2. Matches task domain keywords against skill domain entries
3. Selects ≤3 most relevant skills per task
4. Includes selected skill paths as `skill_references` in plan phases
5. Implementation agents read referenced skill files before starting work

## Adding New Skills

Treat skills as code — additions require review:

1. Create pattern file in `skills/patterns/`
2. Add entry to `skills/index.md`
3. Verify file is ≤100 lines
4. Ensure no stale or contradictory patterns
