---
name: designing-workflow-skills
description: "Architects workflow SKILL.md files with numbered phases, routing/safety-gate/task-driven patterns, tool assignment, and progressive disclosure. Use when building or reviewing a multi-step skill structure rather than its domain content. Not for Cursor skill scaffolding (create-skill) or hermes-agent in-repo authoring (hermes-agent-skill-authoring)."
version: 1.0.1
---

# Designing Workflow Skills

Build workflow-based skills that execute reliably by following structural patterns, not prose. This is a meta-skill: it teaches skill architecture, not domain expertise.

## Overview

Workflow skills are SKILL.md files that guide an agent through multi-step, phased, or routed execution. Reliability comes from structure—numbered phases, entry/exit criteria, tool assignment, and progressive disclosure—not from prose that assumes the LLM will infer ordering or intent.

This skill covers five workflow patterns, twenty anti-patterns, tool assignment rules, and a six-phase creation process. Detailed references live one hop deep in `references/` and `workflows/`.

## Essential Principles

1. **The `description` field is the only thing that controls when a skill activates.** Claude decides whether to load a skill based solely on its frontmatter `description`. The body—including "When to Use" and "When NOT to Use"—is only read AFTER activation. Put trigger keywords, use cases, and exclusions in the description. A bad description means wrong or missed activations regardless of body content. "When NOT to Use" should name specific alternatives: "use Semgrep for simple pattern matching" not "not for simple tasks."

2. **Phases must be numbered with entry and exit criteria.** Unnumbered prose produces unreliable execution order. Every phase needs: a number (Phase 1, Phase 2, ...), entry criteria (what must be true before starting), numbered actions (what to do), and exit criteria (how to know it's done).

3. **Tools must match the executor.** Skills use `allowed-tools:` in frontmatter. Agents use `tools:` in frontmatter. Subagents get tools from their `subagent_type`. Never list tools the component doesn't use. Never use Bash for operations that have dedicated tools (Glob, Grep, Read, Write, Edit). Most skills and agents should include `TodoRead` and `TodoWrite` for progress tracking during multi-step execution.

4. **Progressive disclosure is structural, not optional.** SKILL.md stays under 500 lines. It contains only what the LLM needs for every invocation: principles, routing, quick references, and links. Detailed patterns go in `references/`. Step-by-step processes go in `workflows/`. One level deep—no reference chains (A → B → C). All files are one hop from SKILL.md.

5. **Instructions must produce tool-calling patterns that scale.** Every workflow instruction becomes tool calls at runtime. If a workflow searches N files for M patterns, combine into one regex, not N×M calls. If a workflow spawns subagents per item, use batching, not one subagent per file. Apply the 10,000-file test: mentally run the workflow against a large repo and check that tool call count stays bounded. See AP-18 and AP-19 in the anti-pattern table below.

6. **Match instruction specificity to task fragility.** Calibrate per step:
   - **Low freedom** (exact commands, no variation): Fragile operations—database migrations, crypto, destructive actions. "Run exactly this script."
   - **Medium freedom** (pseudocode with parameters): Preferred patterns where variation is acceptable. "Use this template and customize as needed."
   - **High freedom** (heuristics and judgment): Variable tasks—code review, exploration, documentation. "Analyze the structure and suggest improvements."
   - A skill can mix freedom levels. A security audit skill might use high freedom for discovery and low freedom for reporting.

## When to Use

- Designing a new skill with multi-step workflows or phased execution
- Creating a skill that routes between multiple independent tasks
- Building a skill with safety gates (destructive actions requiring confirmation)
- Structuring a skill that uses subagents or task tracking
- Reviewing or refactoring an existing workflow skill for quality
- Deciding how to split content between SKILL.md, `references/`, and `workflows/`

## When NOT to Use

- Simple single-purpose skills with no workflow (just guidance)—write the SKILL.md directly
- Writing the actual domain content of a skill—this teaches structure, not domain expertise
- Plugin configuration (plugin.json, hooks, commands)—use plugin development guides
- Non-skill agent development—this is specifically for skill architecture

## Prerequisites

- Familiarity with SKILL.md frontmatter fields (`name`, `description`, `allowed-tools`)
- Access to the skill's target codebase or domain context
- Pattern, anti-pattern, tool-assignment, and progressive-disclosure guidance in this skill (companion files are not required)

## Procedure

### Phase 1: Select a Pattern

**Entry criteria:** You know the skill's purpose and have a rough scope.

1. Determine how many distinct execution paths the skill has using the decision tree below.
2. Read the pattern table in this phase before committing to a pattern.

```
How many distinct paths does the skill have?
|
+-- One path, always the same
|   +-- Does it perform destructive actions?
|       +-- YES -> Safety Gate Pattern
|       +-- NO  -> Linear Progression Pattern
|
+-- Multiple independent paths from shared setup
|   +-- Routing Pattern
|
+-- Multiple dependent steps in sequence
    +-- Do steps have complex dependencies?
        +-- YES -> Task-Driven Pattern
        +-- NO  -> Sequential Pipeline Pattern
```

| Pattern | Use When | Key Feature |
|---------|----------|-------------|
| **Routing** | Multiple independent tasks from shared intake | Routing table maps intent to workflow files |
| **Sequential Pipeline** | Dependent steps, each feeding the next | Auto-detection may resume from partial progress |
| **Linear Progression** | Single path, same every time | Numbered phases with entry/exit criteria |
| **Safety Gate** | Destructive/irreversible actions | Two confirmation gates before execution |
| **Task-Driven** | Complex dependencies, partial failure tolerance | TaskCreate/TaskUpdate with dependency tracking |

**Exit criteria:** A pattern name is chosen and its skeleton from the pattern table above has been reviewed.

### Phase 2: Write the Frontmatter

**Entry criteria:** Pattern is selected.

1. Write `name` in kebab-case.
2. Write `description` in third person with specific trigger keywords. This is the ONLY field that controls activation. Never summarize workflow steps in the description (AP-20).
3. List `allowed-tools` (space-delimited). Include only tools the instructions actually reference. Use the tool assignment matrix below. Include `TodoRead` and `TodoWrite` for multi-step skills.
4. Add optional fields only if needed:
   - `disable-model-invocation: true` — only user can invoke (not Claude)
   - `user-invocable: false` — only Claude can invoke (hidden from `/` menu)
   - `context: fork` — run in isolated subagent context
   - `agent: Explore` — subagent type (requires `context: fork`)
   - `model: [model-name]` — switch model when skill is active
   - `argument-hint: "[filename]"` — hint shown during autocomplete

**Exit criteria:** Frontmatter is complete with correct tool list and trigger-optimized description.

### Phase 3: Write the Body

**Entry criteria:** Frontmatter is complete.

1. Write `## Essential Principles` — 3–5 non-negotiable rules with WHY explanations.
2. Write `## When to Use` — 4–6 specific scenarios that scope behavior after activation.
3. Write `## When NOT to Use` — 3–5 scenarios with named alternatives.
4. Write the pattern-specific section (routing table, pipeline steps, phase list, or gates).
5. Write `## Quick Reference` — compact tables for frequently-needed info.
6. Write `## Reference Index` — links to all supporting files in `references/` and `workflows/`.
7. Write `## Success Criteria` — checklist for output validation.
8. Keep total under 500 lines. Move details to `references/`, step-by-step processes to `workflows/`.

**Exit criteria:** Body is complete, under 500 lines, and all file references resolve.

### Phase 4: Assign Tools

**Entry criteria:** Body is written and you know which operations the skill performs.

1. Map component type to tool set using the matrix below.
2. Remove any tool not actually referenced in the instructions (AP-12).
3. Verify read-only components never include `Write` or `Bash`.
4. Use Glob (not `find`), Grep (not `grep`), Read (not `cat`)—always prefer dedicated tools (AP-11).

| Component Type | Typical Tools |
|---------------|---------------|
| Read-only analysis skill | Read, Glob, Grep, TodoRead, TodoWrite |
| Interactive analysis skill | Read, Glob, Grep, AskUserQuestion, TodoRead, TodoWrite |
| Code generation skill | Read, Glob, Grep, Write, Bash, TodoRead, TodoWrite |
| Pipeline skill | Read, Write, Glob, Grep, Bash, AskUserQuestion, Task, TaskCreate, TaskList, TaskUpdate, TodoRead, TodoWrite |
| Read-only agent | Read, Grep, Glob, TodoRead, TodoWrite |
| Action agent | Read, Grep, Glob, Write, Bash, TodoRead, TodoWrite |

**Exit criteria:** Tool list is minimal, correct, and matches the executor type.

### Phase 5: Check Anti-Patterns

**Entry criteria:** Skill is drafted.

1. Review all 20 anti-patterns in the table below.
2. Run through the quick reference table below for the most common mistakes.
3. Fix any violations found.

| AP | Anti-Pattern | One-Line Fix |
|----|-------------|-------------|
| AP-1 | Missing goals/anti-goals | Add When to Use AND When NOT to Use sections |
| AP-2 | Monolithic SKILL.md (>500 lines) | Split into `references/` and `workflows/` |
| AP-3 | Reference chains (A → B → C) | All files one hop from SKILL.md |
| AP-4 | Hardcoded paths | Use `{baseDir}` for all internal paths |
| AP-5 | Broken file references | Verify every path resolves before submitting |
| AP-6 | Unnumbered phases | Number every phase with entry/exit criteria |
| AP-7 | Missing exit criteria | Define what "done" means for every phase |
| AP-8 | No verification step | Add validation at the end of every workflow |
| AP-9 | Vague routing keywords | Use distinctive keywords per workflow route |
| AP-11 | Wrong tool for the job | Use Glob/Grep/Read, not Bash equivalents |
| AP-12 | Overprivileged tools | Remove tools not actually used |
| AP-13 | Vague subagent prompts | Specify what to analyze, look for, and return |
| AP-15 | Reference dumps | Teach judgment, not raw documentation |
| AP-16 | Missing rationalizations | Add "Rationalizations to Reject" for audit skills |
| AP-17 | No concrete examples | Show input → output for key instructions |
| AP-18 | Cartesian product tool calls | Combine patterns into single regex, grep once, then filter |
| AP-19 | Unbounded subagent spawning | Batch items into groups, one subagent per batch |
| AP-20 | Description summarizes workflow | Description = triggering conditions only, never workflow steps |

**Exit criteria:** No anti-pattern violations remain.

### Phase 6: Self-Review

**Entry criteria:** Anti-patterns are fixed.

1. Load `workflows/review-checklist.md` and run through the full structured self-review.
2. Verify every file reference resolves (no broken links).
3. Verify no hardcoded paths—all internal paths use `{baseDir}`.
4. Run the 10,000-file test: mentally execute the workflow against a large repo and confirm tool call count stays bounded.
5. Confirm the description would trigger correctly for the intended use cases and NOT trigger for excluded cases.

**Exit criteria:** All checklist items pass.

## Structural Anatomy

Every workflow skill needs this skeleton, regardless of pattern:

```markdown
---
name: kebab-case-name
description: "Third-person description with trigger keywords — this is how Claude decides to activate the skill"
allowed-tools: Tool1 Tool2 Tool3
---

# Title

## Essential Principles
[3-5 non-negotiable rules with WHY explanations]

## When to Use
[4-6 specific scenarios — scopes behavior after activation]

## When NOT to Use
[3-5 scenarios with named alternatives — scopes behavior after activation]

## [Pattern-Specific Section]
[Routing table / Pipeline steps / Phase list / Gates]

## Quick Reference
[Compact tables for frequently-needed info]

## Reference Index
[Links to all supporting files]

## Success Criteria
[Checklist for output validation]
```

Skills support string substitutions: dollar-prefixed variables for arguments and session ID, and exclamation-backtick syntax for shell preprocessing. The skill loader processes these before Claude sees the file—even inside code fences—so never use the raw syntax in documentation text. See the tool assignment matrix in Phase 4 for the full variable reference.

## Rationalizations to Reject

| Rationalization | Why It's Wrong |
|-----------------|----------------|
| "It's obvious which phase comes next" | LLMs don't infer ordering from prose. Number the phases. |
| "Exit criteria are implied" | Implied criteria are skipped criteria. Write them explicitly. |
| "One big SKILL.md is simpler" | Simpler to write, worse to execute. The LLM loses focus past 500 lines. |
| "The description doesn't matter much" | The description is how the skill gets triggered. A bad description means wrong or missed activations. |
| "Bash can do everything" | Bash file operations are fragile. Dedicated tools handle encoding, permissions, and formatting better. |
| "The LLM will figure out the tools" | It will guess wrong. Specify exactly which tool for each operation. |
| "I'll add details later" | Incomplete skills ship incomplete. Design fully before writing. |

## Pitfalls

- **Description summarizes the workflow instead of stating trigger conditions.** The description is a trigger, not a summary. Write "Use when reviewing code for security vulnerabilities, injection risks, and auth bypass" not "This skill runs a 5-phase security audit with static analysis and reporting."

- **Unnumbered phases cause out-of-order execution.** LLMs do not infer sequence from prose structure. Every phase must have an explicit number, entry criteria, and exit criteria.

- **Reference chains (A → B → C) lose context.** Each hop forces the LLM to reload context. All reference files must be exactly one hop from SKILL.md. If a reference needs to reference another file, inline the content instead.

- **Hardcoded paths break portability.** Use `{baseDir}` for all internal paths. Never hardcode `~` or `/home/...` paths in skill files.

- **Overprivileged tool lists cause unintended actions.** A read-only analysis skill with `Bash` can accidentally execute destructive commands. List only the tools the instructions actually reference.

- **Cartesian product tool calls don't scale.** If a workflow searches N files for M patterns, writing N×M individual calls will exhaust context on large repos. Combine into a single regex or batch operation. Apply the 10,000-file test.

- **Unbounded subagent spawning exhausts resources.** If a workflow spawns one subagent per file, a 10,000-file repo will hang. Batch items into groups and spawn one subagent per batch.

- **String substitution syntax leaks into documentation.** The skill loader processes `$variable` and `` !`command` `` syntax before Claude sees the file, even inside code fences. Never use the raw syntax when documenting it—escape or describe it indirectly.

## Verification

After designing a workflow skill, verify:

1. **Frontmatter check:**
   ```powershell
   Select-String -Path "SKILL.md" -Pattern "^name:" | ForEach-Object { $_.Line }
   Select-String -Path "SKILL.md" -Pattern "^description:" | ForEach-Object { $_.Line }
   Select-String -Path "SKILL.md" -Pattern "^allowed-tools:" | ForEach-Object { $_.Line }
   ```
   Confirm `name` is kebab-case, `description` contains trigger keywords (not workflow summary), and `allowed-tools` lists only used tools.

2. **Line count check (must be under 500):**
   ```powershell
   (Get-Content "SKILL.md").Count
   ```

3. **File reference resolution:**
   ```powershell
   Select-String -Path "SKILL.md" -Pattern '\[.*?\]\((references|workflows)/.*?\.md\)' -AllMatches |
     ForEach-Object { $_.Matches } |
     ForEach-Object { $_.Groups[1].Value + "/" + $_.Value } |
     ForEach-Object { if (-not (Test-Path $_)) { Write-Output "BROKEN: $_" } }
   ```
   Output should be empty—no broken references.

4. **Hardcoded path check:**
   ```powershell
   Select-String -Path "SKILL.md" -Pattern 'C:\\Users\\|/home/|/Users/' |
     ForEach-Object { Write-Output "HARDCODED: $($_.LineNumber): $($_.Line)" }
   ```
   Output should be empty (unless documenting a specific machine path by design).

5. **Reference chain check:** Manually open each file in `references/` and `workflows/` and confirm none link to another reference file. All links must point back to SKILL.md or external URLs only.

6. **Success criteria checklist:**
   - [ ] Has When to Use AND When NOT to Use sections
   - [ ] Uses a recognizable pattern (routing, pipeline, linear, safety gate, or task-driven)
   - [ ] Numbers all phases with entry and exit criteria
   - [ ] Lists only the tools it actually uses (least privilege)
   - [ ] Keeps SKILL.md under 500 lines with details split into companion reference and workflow files
   - [ ] Has no hardcoded paths (uses `{baseDir}`)
   - [ ] Has no broken file references
   - [ ] Has no reference chains (all links one hop from SKILL.md)
   - [ ] Includes a verification step at the end of the workflow
   - [ ] Has a description that triggers correctly (third-person, specific keywords)
   - [ ] Includes concrete examples for key instructions
   - [ ] Explains WHY, not just WHAT, for essential principles

## Reference Index

| Topic | Content | When to use |
|------|---------|--------------|
| Workflow patterns | 5 patterns with structural skeletons and examples | Phase 1: before selecting a pattern (table above) |
| Anti-patterns | 20 anti-patterns with before/after fixes | Phase 5: before reviewing the draft (table above) |
| Tool assignment | Tool selection matrix, component comparison, subagent guidance | Phase 4: when assigning tools |
| Progressive disclosure | Content splitting rules, the 500-line rule, sizing guidelines | Phase 3 / Essential Principle 4 |
| Creation process | 6-phase creation from scope to self-review | Phases 1–6 in this skill |
| Self-review | Structured checklist for submission readiness | Phase 6 and Verification below |

## Related Skills

- **progressive-disclosure-guide** — Content splitting rules and the 500-line rule
- **tool-assignment-guide** — Tool selection matrix and subagent guidance
- **anti-patterns** — Full catalog of 20 anti-patterns with fixes
