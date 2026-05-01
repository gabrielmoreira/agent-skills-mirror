---
name: dde-ext-brainstorm
description: "DDE subordinate extension. Multi-solution ideation and tradeoff analysis before plan/implementation. Advisory-only, write-gated by DDE."
---

# DDE Extension: Brainstorm

Skill Version: v0.1

## Authority Chain
- Commander: `dde-bootstrap`
- Write gate: `dde-code-guard`
- Completion gate: `dde-task-closer`
- This skill is advisory-only and cannot modify files directly.

## When to Use
Use this skill when:
- User asks for: `brainstorm`, `ideation`, `options`, `tradeoff`, `alternatives`
- User asks for: `头脑风暴`, `方案对比`, `思路发散`, `可行性讨论`, `怎么选方案`
- Requirement has multiple feasible paths and needs decision support before implementation
- DDE workflow explicitly selects ideation mode

## Do Not Use When
- User explicitly requests direct file modifications now
- Task is deterministic mechanical edit with no decision branches
- A final approved plan already exists and user asks to execute immediately

## Hard Constraints
1. Advisory-only: no writes to code/docs/skills in this skill.
2. No requirement authority takeover: Layer 0-4 remains source of truth.
3. If a proposed direction conflicts with Layer docs, emit `RFC_REQUIRED` and stop for DDE RFC flow.
4. If user chooses a direction that requires edits, emit handoff only and return control to `dde-code-guard`.

## Workflow

### Phase 1: Problem Framing
- Restate objective in 1-3 lines.
- List constraints (performance, safety, timeline, compatibility).
- Mark unknowns and assumptions explicitly:
  - `ASSUMPTION: ...`

### Phase 2: Option Generation
Generate at least 2 options (prefer 3):
- Option A: conservative / low-risk
- Option B: balanced / default
- Option C: aggressive / high-upside (optional)

For each option include:
- Core idea
- Required changes (high-level)
- Dependencies/tools needed
- Risks/failure modes
- Cost (time/complexity)
- Expected benefit

### Phase 3: Tradeoff Matrix
Provide side-by-side matrix scored 1-5:
- feasibility
- implementation effort
- maintainability
- scalability
- risk level (inverse score: lower risk = higher score)
- alignment with Layer docs

### Phase 4: Recommendation
- Recommend one option with rationale.
- Provide fallback option.
- List decision locks (what must stay true for this recommendation to hold).

### Phase 5: Decision Gate
Ask user to select:
- `SELECTED_OPTION: A|B|C`
- or request refinement round.

If selection implies requirement/document change:
- emit `RFC_REQUIRED` and stop for DDE RFC flow.

If selection implies code/doc writes without requirement conflict:
- emit `DDE_EXTENSION_HANDOFF_REQUIRED` and transfer to `dde-code-guard`.

### Phase 6: Decision Artifact Contract
When user confirms selected option, produce a DDR draft (without writing files in this skill) using this target convention:
- `docs/decisions/DDR-YYYYMMDD-<topic>.md`
- Template source priority:
  1. Project instance: `docs/decisions/DDR_TEMPLATE.md`
  2. Skill template fallback: `templates/DDR_TEMPLATE.md`

DDR required fields:
- Decision Question
- Options Considered
- Selected Option
- Why Selected
- Impacted Files

## Output Contract (Mandatory)
Output in this exact structure:
1. `BRAINSTORM BRIEF`
2. `ASSUMPTIONS`
3. `OPTIONS`
4. `TRADEOFF MATRIX`
5. `RECOMMENDATION`
6. `DECISION REQUEST`
7. `HANDOFF STATUS`

Where `HANDOFF STATUS` is one of:
- `NO_WRITE_NEEDED`
- `RFC_REQUIRED`
- `DDE_EXTENSION_HANDOFF_REQUIRED`

## Handoff Block Format
When handoff is required, append:

`DDE_EXTENSION_HANDOFF_REQUIRED`

Fields:
- Reason
- Selected option
- Target files (if known)
- Expected effect
- Risk notes
- Rollback note (high-level)
