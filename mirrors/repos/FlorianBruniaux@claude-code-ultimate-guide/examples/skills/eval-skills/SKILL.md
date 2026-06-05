---
name: eval-skills
description: "Audit all skills in the current project for frontmatter completeness, effort level appropriateness, allowed-tools scoping, and content quality. Produces a scored report with effort-level recommendations for each skill. Use when onboarding to a new project, reviewing skill quality before shipping, or adding effort fields to an existing skill library."
when_to_use: "Trigger phrases: 'audit my skills', 'check skill quality', 'review skills', 'score skills', 'eval skills'. Also use when a user asks why Claude isn't triggering a skill automatically."
allowed-tools: Read Glob Bash
argument-hint: "[path (default: .claude/skills/)]"
effort: medium
---

# Skill Evaluator

Discover all skills in the project, score them across 6 criteria, and infer the appropriate `effort` level based on content analysis.

## When to Use

- New project: run once to establish baseline quality
- Before committing a skill to a team repo
- After bulk-importing skills from another project
- When adding `effort` fields for the first time
- When a skill doesn't auto-trigger and you want to diagnose why

## What Gets Audited

All `SKILL.md` files and flat `.md` files found in:
- `.claude/skills/**`
- `~/.claude/skills/**` (if requested)
- `.claude/commands/**` (legacy flat files, still valid)
- Any path passed as argument: `/eval-skills ./my-skills-dir`

---

## Valid Frontmatter Fields

Claude Code skills follow the [agentskills.io](https://agentskills.io) open standard, extended with Claude Code-specific fields. Flag any field not in this table as unsupported.

### agentskills.io spec fields

| Field | Required | Notes |
|-------|----------|-------|
| `name` | No | Display label shown in skill lists. The command name always comes from the **directory name**, not this field. |
| `description` | Recommended | Combined with `when_to_use`, truncated at **1,536 chars** in context. First paragraph used if omitted. |
| `when_to_use` | No | Additional trigger phrases and example requests. Appended to `description` in context; counts toward the 1,536-char cap. |
| `allowed-tools` | No | Tools usable without per-use approval while the skill is active. Space-separated string or YAML list (both valid). |
| `license` | No | License identifier (agentskills.io spec) |
| `compatibility` | No | Compatibility constraints (agentskills.io spec) |
| `metadata` | No | Arbitrary metadata object (agentskills.io spec) |

### Claude Code extension fields

| Field | Required | Notes |
|-------|----------|-------|
| `argument-hint` | No | Hint shown during autocomplete. Example: `[issue-number]` or `[filename] [format]` |
| `arguments` | No | Named positional args for `$name` substitution. Space-separated string or YAML list. Names map to positions in order. |
| `disable-model-invocation` | No | `true` = user-only invocation. Removes skill from Claude's context and prevents preloading in subagents. |
| `user-invocable` | No | `false` = hides skill from `/` menu but Claude can still auto-invoke it. |
| `disallowed-tools` | No | Tools blocked while this skill is active. Cleared after the current message. |
| `model` | No | Override model for this skill's turn only. Reverts to session model on next prompt. |
| `effort` | No | Thinking effort: `low`, `medium`, `high`, `xhigh`, `max`. Overrides session effort for the turn. |
| `context` | No | `fork` = runs skill in an isolated subagent context. The skill body becomes the subagent's prompt. |
| `agent` | No | Which subagent type to use when `context: fork` is set. Options: `Explore`, `Plan`, `general-purpose`, or any custom agent in `.claude/agents/`. |
| `hooks` | No | Skill-scoped lifecycle hooks. Same format as session hooks. |
| `paths` | No | Glob patterns that limit when Claude auto-loads this skill. Same format as path-specific rules. |
| `shell` | No | Shell for `!backtick` injection: `bash` (default) or `powershell`. |

### Unsupported fields (flag and remove)

`tags`, `category`, `keywords`, `usage`, `args` are ignored by the runtime. Remove them to avoid confusion.

---

## String Substitutions (check for correct usage)

If a skill references substitution placeholders, verify they use the correct syntax:

| Placeholder | Meaning |
|-------------|---------|
| `$ARGUMENTS` | Full argument string as typed |
| `$ARGUMENTS[N]` or `$N` | Argument at position N (0-based) |
| `$name` | Named argument declared in `arguments:` frontmatter |
| `${CLAUDE_SESSION_ID}` | Current session ID |
| `${CLAUDE_EFFORT}` | Active effort level (`low` / `medium` / `high` / `xhigh` / `max`) |
| `${CLAUDE_SKILL_DIR}` | Absolute path to the skill's directory; use it for referencing bundled scripts |

Incorrect placeholders (`$1` when no `arguments:` field is declared, `${ARGS}`, `%ARGUMENTS%`) are passed as literal text and silently break the skill.

---

## Scoring Criteria (16 pts per skill)

| # | Criterion | Max | What is checked |
|---|-----------|-----|-----------------|
| 1 | **name field** | 1 | `name` field present and lowercase with hyphens only |
| 2 | **description** | 3 | Present (1), has "Use when" / trigger phrasing (1), `when_to_use` field present for skills that need broad matching (1) |
| 3 | **allowed-tools** | 2 | Present (1), scoped appropriately (1): not `Bash` without path scoping when read-only tools suffice |
| 4 | **effort** | 3 | Present (1), appropriate for content per inference engine below (2) |
| 5 | **content structure** | 5 | Has Purpose or When section (1), has concrete examples or usage (1), has clear workflow or steps (1), no placeholder text (1), no unsupported frontmatter fields (1) |
| 6 | **bonus** | +2 | `argument-hint` present when skill takes args (1), `${CLAUDE_SKILL_DIR}` used for bundled scripts instead of hardcoded paths (1) |

**Thresholds:**
- ✅ Good: >=13/16 (>=80%)
- ⚠️ Needs work: 10-12/16 (60-79%)
- ❌ Fix: <10/16 (<60%)

### `allowed-tools` format note

Both formats are valid and parse correctly:
- Space-separated string: `Read Bash Grep`
- YAML list: `[Read, Bash, Grep]`

Flag skills that use `Bash` globally (without path scoping like `Bash(git *)`) when they only need read operations (this grants unnecessary write access).

### description length note

The combined `description` + `when_to_use` text is truncated at **1,536 chars** per skill in Claude's context. Flag skills where the combined text exceeds this limit; the tail (often the trigger examples) gets silently cut.

---

## Effort Level Inference Engine

For each skill, analyze description + content and classify using these signals:

### `low`: Mechanical execution, no design decisions

Signals:
- Verbs: commit, push, sync, scaffold, generate (template-based), format, rename, bump, wrap, convert
- No reasoning required: sequential steps, template instantiation, data fetching
- `allowed-tools`: `Bash` only, or `Read` only
- No sub-agents spawned
- Short workflow (<5 steps)

Examples: `/commit`, `/release-notes`, `/scaffold`, `/sync`, `/format`

### `medium`: Analysis with bounded scope, categorization

Signals:
- Verbs: review, triage, analyze, categorize, suggest, evaluate (single file or bounded scope)
- Requires pattern recognition but not architectural reasoning
- `allowed-tools`: `Read` + `Grep` + `Bash` combination
- May spawn 1-2 sub-agents with predefined scope
- Produces structured output (tables, categorized lists)

Examples: `/code-review` (single PR), `/issue-triage`, `/dependency-audit`, `/test-coverage`

### `high`: Design decisions, adversarial reasoning, cross-system analysis

Signals:
- Verbs: architect, redesign, threat-model, audit (security), orchestrate (multi-agent), score, assess trade-offs
- Requires reasoning about edge cases, attack vectors, or system-wide implications
- `allowed-tools`: broad access (`Read` + `Write` + `Bash` + external tools)
- Spawns multiple sub-agents or uses parallel execution
- Produces analysis with explicit uncertainty or trade-off sections
- Keywords: "security", "architecture", "adversarial", "pipeline", "threat", "design decision"

Examples: `/security-audit`, `/architecture-review`, `/eval-agents`

### `xhigh` / `max`: Exhaustive, multi-agent, long-running

Signals:
- Explicit `ultrathink` or `ultracode` in skill body
- Spawns many parallel agents (3+)
- Uses `Workflow` tool or fan-out orchestration patterns
- Expected runtime >5 minutes
- Deep synthesis across entire codebase or multi-repo scope

Examples: `/deep-research`, `/full-security-audit`, `/codebase-migration`

### Mismatch flag

If a skill has `effort:` already set but the inferred level differs, flag it:
> ⚠️ Effort mismatch: declared `low`, inferred `high`. Skill spawns 4 sub-agents and performs security analysis.

---

## Execution Instructions

### Step 1: Discovery

```bash
# Find all SKILL.md files
find .claude/skills -name "SKILL.md" 2>/dev/null

# Find legacy flat command files
find .claude/commands -maxdepth 1 -name "*.md" ! -name "README*" 2>/dev/null

# If argument provided, use that path instead
```

### Step 2: Parse each skill

For each skill file found:
1. Read the full file
2. Extract YAML frontmatter (between first `---` and second `---`)
3. Parse all recognized fields from the table above
4. Flag any unrecognized fields as potentially unsupported
5. Note presence/absence of each field
6. Read the body content for structure analysis and substitution placeholder correctness

### Step 3: Score and infer

Apply the scoring criteria to each skill:
- Check frontmatter fields against the valid fields table
- Evaluate description quality: does it answer "when to use"? Is combined description + when_to_use under 1,536 chars?
- Evaluate `allowed-tools` scope: is `Bash` used without path scoping when read-only tools suffice?
- Check `context: fork` skills for completeness; they must have an actionable task body and an `agent` field (or a reasonable default applies)
- Infer effort level from content analysis
- Compare inferred vs declared effort (if set)
- Evaluate content structure

### Step 4: Output

Produce a structured report:

```
# Skills Audit: [project name or path]
Date: [today] | Scanned: N skills

## Summary
| Status | Count |
|--------|-------|
| ✅ Good (>=80%) | N |
| ⚠️ Needs work (60-79%) | N |
| ❌ Fix (<60%) | N |

**Effort coverage**: N/N skills have effort field set

---

## Per-Skill Results

### [skill-name] ([score]/16) [✅/⚠️/❌]

| Criterion | Score | Notes |
|-----------|-------|-------|
| name | ✅ 1/1 | ok |
| description | ⚠️ 2/3 | Missing when_to_use field |
| allowed-tools | ✅ 2/2 | Well-scoped |
| effort | ❌ 0/3 | Missing. Recommended: high |
| content structure | ⚠️ 3/5 | No examples section, unsupported field "tags" found |

**Effort inference**: `high`. Skill performs security analysis with adversarial reasoning.
  Signals: "threat", "attack surface", "vulnerability scoring" in content; spawns 4 agents

**Priority fixes** (ordered by impact):
1. Add `effort: high` to frontmatter
2. Add `when_to_use` with trigger phrases
3. Remove unsupported field `tags`
4. Add a concrete usage example section

---
```

After all skills: print a **Fix Summary**.

---

## Fix Summary Format

At the end, print a ready-to-use patch block for all missing/mismatched effort fields:

```
## Recommended effort fields (copy-paste ready)

skill-name-1: effort: low     # mechanical scaffold
skill-name-2: effort: high    # security analysis, spawns agents
skill-name-3: effort: medium  # code review, bounded scope
```

And a 1-line count: `N skills need effort field · N mismatches · N missing allowed-tools · N unsupported fields to remove`
