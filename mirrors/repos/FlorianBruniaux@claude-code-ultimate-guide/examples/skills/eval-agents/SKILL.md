---
name: eval-agents
description: "Audit Claude Code agents defined in .claude/agents/ for description specificity, model tier appropriateness, tools scoping, and system prompt quality. Detects dispatch ambiguity between agents, flags over-permissive tool grants, and checks for human-in-the-loop patterns that break programmatic orchestration. Use when onboarding to a project with existing agents, after adding new agents to a fleet, or when an orchestrator consistently selects the wrong agent."
allowed-tools: Read Glob Bash Edit
effort: medium
argument-hint: "[path to agents dir, default: .claude/agents/]"
---

# Agent Evaluator

Discover all agents in scope, score each one across five criteria, then run an interactive session to confirm or improve them one by one.

Agents are not just scripts: they are callable units selected by orchestrators based on their description. A vague description silently breaks multi-agent workflows. The goal here is not just scoring; it is leaving every agent correctly scoped, correctly modeled, and safe to call from an orchestrator.

## When to Use

- First time auditing an agent fleet before wiring it into an orchestration pipeline
- An orchestrator keeps selecting the wrong agent for a task
- After copying agents from another project or importing a plugin
- A new agent was added; checking whether it conflicts with existing ones
- Periodic hygiene: "do all these agents still do something distinct?"

## Key Concepts

### Agent file locations

| Location | Scope | Committed? |
|---|---|---|
| `.claude/agents/<name>.md` | Project (flat file) | Yes |
| `.claude/agents/<name>/AGENT.md` | Project (directory-based) | Yes |
| `~/.claude/agents/<name>.md` | User-level | No |
| Plugin `agents/*.md` | Per plugin | Yes (in plugin) |

Both flat files and directory-based agents are valid. The `name:` field is the identifier used by orchestrators and hooks (passed as `agent_type`). The filename does not have to match, though keeping them aligned is recommended.

### Frontmatter fields

| Field | Required | Notes |
|---|---|---|
| `name` | Yes | Unique identifier (kebab-case). Hooks receive this as `agent_type`. Filename does not have to match. |
| `description` | Yes | Used by orchestrators to select agents. Vague = wrong agent selected. |
| `model` | No | Defaults to session model if absent. Explicit is always better. |
| `tools` | No | Explicit tool allow-list. Defaults to session tools if absent (risky). Note: `allowed-tools` is the equivalent field for skill files (not valid in agent files). |
| `disallowedTools` | No | Blocks specific tools even if granted by the session. |
| `permissionMode` | No | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`. Flag `bypassPermissions` as a security risk equivalent to unconstrained tools. |
| `effort` | No | `low`, `medium`, `high`, `xhigh`, `max`. Overrides session effort. |
| `isolation` | No | `worktree` runs the agent in a temporary git worktree (isolated copy of the repo). |
| `maxTurns` | No | Maximum agentic turns before the agent stops. Prevents runaway loops in pipelines. |
| `memory` | No | `user`, `project`, or `local`. Persistent cross-session memory directory. |
| `background` | No | `true` always runs this agent as a background task. |

### Why description quality matters more for agents than for skills

Skills are invoked by humans typing a slash command. Agents are selected programmatically by orchestrators comparing all candidate descriptions against a task. Two agents with similar descriptions produce non-deterministic selection; the orchestrator will flip between them across runs, giving inconsistent results. Description overlap is a correctness bug, not a style issue.

Good agent description pattern:
```
"Use when X and NOT Y. Handles Z. Returns [format]."
```

Weak pattern:
```
"Helps with code quality and review."
```

### Model tier selection

| Task type | Model | Signals |
|---|---|---|
| Mechanical: lookup, pattern match, binary pass/fail | `haiku` | grep results, count files, extract value, apply template |
| Judgment: review, analyze, write, debug (bounded scope) | `sonnet` | code review, test writing, documentation, diagnosis |
| Deep synthesis: architecture, adversarial, cross-system | `opus` | security audit, ADR generation, system design review |

Using `opus` for a task that only needs `haiku` burns 20-50x more tokens per call. In a pipeline that calls an agent 100 times, that becomes expensive. Flag model-task mismatches both directions: under-powered (produces shallow output) and over-powered (wastes budget).

### Human-in-the-loop anti-patterns

Agents called from orchestrators run headlessly. Any system prompt instruction that assumes a human is watching will silently break or stall the pipeline:

| Anti-pattern | What breaks |
|---|---|
| "Ask the user for clarification" | Agent blocks waiting for input that never comes |
| "Confirm before deleting" | Same: no confirmation possible |
| "Show results and wait for approval" | Orchestrator receives no output, times out |
| "If unsure, ask" | Produces empty output instead of best-effort result |

Safe alternative: "If context is insufficient, return `{ "status": "needs_context", "missing": [...] }` and stop."

---

## Scoring Criteria (15 pts per agent)

| # | Criterion | Max | What is checked |
|---|-----------|-----|-----------------|
| 1 | **name** | 1 | `name` field present and uses kebab-case; recommend matching the filename for clarity |
| 2 | **description** | 4 | Present (1pt), contains trigger phrasing specifying WHEN to use (1pt), specific enough to distinguish from other agents in the same fleet (1pt), concise and front-loaded with the most important triggers first (1pt) |
| 3 | **model** | 2 | Present (1pt), appropriate tier for task complexity using matrix above (1pt) |
| 4 | **tools** | 3 | `tools` field present and explicit (1pt), no `*` wildcard without written justification in the system prompt (1pt), write-capable tools (`Bash`, `Edit`, `Write`) only present when the agent's task requires file mutation (1pt) |
| 5 | **system prompt** | 5 | Has role/scope statement in first paragraph (1pt), defines task boundaries (what it does AND does not do) (1pt), specifies output format or return contract (1pt), no placeholder text or TODO comments (1pt), no human-in-the-loop patterns from the table above (1pt) |
| Bonus | **hardening** | +1 | `effort` field present and inferred-appropriate for task complexity |

**Thresholds:**
- Good: >=12/15 (>=80%)
- Needs work: 9-11/15 (60-79%)
- Fix: <9/15 (<60%)

**No-tools agents** (no `tools:` field): they inherit the session tool set, which is usually broader than needed. Treat this as 0/3 on criterion 4 and flag explicitly: unconstrained tool access in a fleet agent is a security surface.

---

## Execution Instructions

### Step 1: Discovery

Find all agent files in scope:

```bash
# Flat files
find .claude/agents -maxdepth 1 -name "*.md" 2>/dev/null

# Directory-based
find .claude/agents -name "AGENT.md" 2>/dev/null

# User-level (only if requested)
find ~/.claude/agents -name "*.md" 2>/dev/null
```

If an argument was passed (e.g., `/eval-agents examples/agents/`), use that path instead.

Build a flat list of agent records:
- `source_file`: path to the `.md` file
- `agent_name`: directory name or filename stem
- `model`: declared model or `(inherits session)`
- `tools`: list of declared tools or `(inherits session)`
- `description_length`: character count of `description` field
- `system_prompt_length`: line count of body after frontmatter

If no agents are found, report it and stop.

### Step 2: Parse and classify

For each agent:
1. Read the full file
2. Extract YAML frontmatter
3. Collect all frontmatter fields (flag any unsupported/unknown fields)
4. Read the body: line count, presence of role statement, output format declaration
5. Scan for human-in-the-loop anti-patterns (keyword scan: "ask the user", "confirm", "wait for approval", "if unsure ask")

### Step 3: Check description overlap

Compare descriptions pairwise across all agents in the same directory:

For each pair (A, B):
- If their `description` fields share more than 3 key nouns or verbs, flag as potential dispatch conflict
- If both use identical trigger phrasing ("Use for code review"), flag as duplicate

Report conflicts as:
```
⚠️ Dispatch conflict: code-reviewer.md ↔ integration-reviewer.md
  Both describe "code review" and "quality checks"; orchestrator may conflate them.
  Suggestion: differentiate by scope (PR diff vs full module vs API surface).
```

### Step 4: Model appropriateness check

For each agent, infer the appropriate model tier from the system prompt content:

**Haiku signals** (mechanical): "extract", "count", "list", "find files matching", "output JSON with fields X Y Z", "grep for", "check if exists", verbs with no judgment required

**Sonnet signals** (judgment): "review", "analyze", "debug", "write tests", "document", "suggest improvements", "classify", bounded scope per invocation

**Opus signals** (deep synthesis): "architect", "threat model", "security audit", "design decision", "evaluate trade-offs across", "cross-cutting", "multi-system", scope spans entire codebase or long-horizon reasoning

Flag mismatches:
- Declared `haiku`, inferred `sonnet` or higher: ⚠️ may produce shallow output
- Declared `opus`, inferred `haiku`: ⚠️ burning 20-50x budget for mechanical work

### Step 5: Interactive review (core of the skill)

Process agents **one by one**. Do not batch and skip the interaction.

**For each agent:**

Show:
```
Agent: code-reviewer.md [.claude/agents/]
model: sonnet
tools: Read, Grep, Glob
description: "Use for thorough code review with quality, security, and performance checks"
System prompt: 67 lines

Inferred model tier: sonnet ✅
Description specificity: ⚠️ overlaps with integration-reviewer.md on "quality checks"
Human-in-the-loop patterns: none found ✅
Write tools: none (read-only) ✅
```

Ask four questions:
1. "Is the description specific enough to distinguish this agent from similar ones? (y = yes / n = rewrite)"
2. "Is the model tier right for what this agent does? (y / change to haiku/sonnet/opus)"
3. "Are the tools correctly scoped? (y / add / remove)"
4. "Anything to update in the system prompt? (describe or skip)"

**If the user provides changes during the interaction**: apply them using Edit, confirm each change, then move to the next agent.

**For agents with no tools field:**

Show:
```
Agent: planner.md [.claude/agents/]
model: (inherits session)
tools: (inherits session, UNCONSTRAINED)
```

Flag strongly: no explicit `tools` field means the agent inherits whatever the calling session has, including write access it may not need. Ask whether to add an explicit `tools:` constraint.

### Step 6: Output report

After all agents are reviewed:

```
# Agents Audit: [project name or path]
Date: [today] | Scanned: N agents

## Summary

| Status | Count |
|--------|-------|
| ✅ Good (>=80%) | N |
| ⚠️ Needs work (60-79%) | N |
| ❌ Fix (<60%) | N |
| ⚠️ Dispatch conflicts detected | N pairs |
| ⚠️ No explicit tools field | N |
| ✅ User confirmed useful | N |
| ⚠️ User flagged for update | N |
| 🗑️ User marked as stale | N |

---

## Per-Agent Results

### code-reviewer.md (11/15 ⚠️)

model: sonnet (inferred: sonnet ✅)
tools: Read, Grep, Glob (read-only ✅)
description length: 63 chars

| Criterion | Score | Notes |
|-----------|-------|-------|
| name | ✅ 1/1 | kebab-case, matches filename |
| description | ⚠️ 2/4 | Present, trigger phrasing ok, but overlaps with integration-reviewer.md; over 1,536 chars |
| model | ✅ 2/2 | sonnet appropriate for bounded code review |
| tools | ✅ 3/3 | explicit, read-only, no wildcard |
| system prompt | ⚠️ 3/5 | role statement present, boundaries defined, no output format specified, no placeholder, no human-in-the-loop patterns |
| hardening (bonus) | ❌ 0/1 | no effort field |

**Priority fixes:**
1. Narrow description to distinguish from integration-reviewer.md (scope: single file/PR diff, not API surface)
2. Add output format contract to system prompt (e.g., returns markdown with severity table)
3. Add `effort: medium`

User feedback: description updated ✅
System prompt: output format added ✅

---
```

### Step 7: Fix Summary

```
## What Changed This Session

code-reviewer.md:
  - Description narrowed: added "PR diff scope, not API surface"
  - System prompt: added output format contract
  - Added effort: medium

planner.md:
  - Added tools: Read, Write (was inheriting session tools)
  - User confirmed model: sonnet is appropriate

security-auditor.md:
  - User flagged as stale (awaiting explicit deletion confirmation)

---
N agents audited · N edits applied · N dispatch conflicts resolved · N flagged as stale
```

For any agent the user marked as stale: ask for explicit confirmation before removing the file. Never delete without a clear "yes, remove it".

---

## Edge Cases

- **No `tools:` field**: agent inherits session tools; flag as 0/3 on tools criterion, always raise in interactive step regardless of other scores
- **`tools: "*"` wildcard**: full session access, treat as equivalent to no tools field unless the system prompt explicitly justifies why unrestricted tools are needed (e.g., a general-purpose agent)
- **`permissionMode: bypassPermissions`**: flag immediately, same severity as an unconstrained tools field; the agent can execute operations without approval including writes to `.git`, `.claude`, and config directories
- **`model` field absent**: flag as ⚠️ in model criterion; add model inference note ("inferred sonnet from content signals")
- **Description under 20 chars**: too vague to be usable for dispatch; flag as 0/4 on description criterion
- **Excessively long description**: no confirmed character limit exists in the official docs; front-load the most important trigger conditions since orchestrators use early tokens for dispatch; flag descriptions over 800 chars as a style warning
- **System prompt under 10 lines**: likely a stub or placeholder; flag for content quality review
- **`isolation: worktree` on a read-only agent**: filesystem isolation is unnecessary when the agent has no write tools (`Edit`, `Write`, `Bash`); flag as redundant overhead and ask whether isolation is intentional
- **Human-in-the-loop pattern in a fork agent**: especially problematic since forked agents have no terminal to interact with; flag as ❌ on system prompt criterion 5
- **Duplicate agent names** (same `name:` field, different files): runtime loads both, last one wins; flag immediately
- **Agent file not readable**: report and skip (may be a permissions issue or empty file)
- **`disallowedTools` with a tool not in `tools`**: redundant but harmless; note it
- **Flat `.claude/agents/` file with same stem as a subdirectory agent**: naming conflict, flag which one the runtime will use
- **Description that says "use for everything" or "general purpose"**: acceptable only for catch-all agents placed intentionally at the bottom of a dispatch priority stack; flag others
- **Two agents with identical `model` and `tools` but different descriptions**: may be legitimate specializations or may be redundant copies from a refactor; surface to user during interactive step