# Skills Library

## Purpose

Reusable domain-specific patterns and best practices for agent consumption. Planner selects relevant skills during planning and includes them as `skill_references` in plan phases. Implementation agents read referenced skills before starting work.

## Directory Structure

```
skills/
├── README.md          # This file — overview and discovery protocol
├── index.md           # Master index mapping domains to skill files
└── patterns/          # Domain-specific pattern files (18 files)
    ├── budget-tracking.md
    ├── code-simplification.md
    ├── completeness-traceability.md
    ├── debugging-discipline.md
    ├── error-handling-patterns.md
    ├── idea-to-prompt.md
    ├── integration-validator.md
    ├── llm-behavior-guidelines.md
    ├── memory-promotion-candidates.md
    ├── orchestration-audit-playbook.md
    ├── performance-patterns.md
    ├── preflect-core.md
    ├── reflection-loop.md
    ├── repo-memory-hygiene.md
    ├── security-patterns.md
    ├── security-review-discipline.md
    ├── spec-driven-development.md
    └── tdd-patterns.md
```

## Format Specification

Pattern files are written for direct agent consumption rather than a single rigid template. The conventions that current files share:

- **Title** — A top-level `# <Skill Name>` heading naming the skill or canonical gate.
- **Purpose** — A `## Purpose` section stating what the skill governs and why an agent loads it. Often pairs with a governance flag or "single source of truth" pointer (e.g. `preflect-core.md`, `repo-memory-hygiene.md`).
- **When to Apply / When to Load** — A section describing the trigger conditions and which agents invoke the skill at which workflow points.
- **Body sections** — Topic-specific `##`/`###` sections tailored to the domain. Common forms include:
  - Numbered or named **checklists** with explicit stop/continue outcomes (e.g. `repo-memory-hygiene.md` Step 1–5).
  - **Decision heuristics** posing a concrete question and branching on the answer (e.g. `tdd-patterns.md`, `preflect-core.md`).
  - **Tables** mapping scope/layer/risk to guidance (e.g. the TDD test-layer matrix).
  - Explicit **anti-pattern** call-outs where useful, but not as a mandatory standalone section.

Sections beyond Title/Purpose are chosen to fit the skill's domain; the older fixed Applicability/Patterns/Anti-Patterns/References template is no longer required.

**Constraint:** Each pattern file must be ≤100 lines to fit within agent context budgets. This cap is enforced by the eval validator.

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
3. Verify file is ≤100 lines (enforced by the validator)
4. Ensure no stale or contradictory patterns
5. Run the verification suite: `cd evals && npm test`
