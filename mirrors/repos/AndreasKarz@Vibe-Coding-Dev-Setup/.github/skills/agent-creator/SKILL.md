---
name: agent-creator
description: "Guide for creating and updating VS Code .agent.md files. Use when a user wants to create a new agent, update an existing agent, or needs help designing an agent's structure, workflow, and domain knowledge sections. Triggers on: create agent, new agent, agent.md, update agent, overhaul agent, agent design."
license: Complete terms in LICENSE.txt
---

# Agent Creator

Create effective `.agent.md` files for VS Code's chat agent system. Agents are specialized personas that combine domain expertise with structured workflows and tool usage.

## Before Creating an Agent

### Fetch Latest Best Practices

Before writing or overhauling any agent, fetch the latest agentic design best practices from Anthropic:

1. Use `fetch_webpage` or `mcp_fetch_fetch` to retrieve:
   **https://anthropic.com/research/building-effective-agents**
2. Extract key principles relevant to the agent being created
3. Apply those principles throughout the agent design

If the URL is unreachable, fall back to the embedded principles below.

### Embedded Agentic Design Principles (Fallback)

These are core principles from Anthropic's "Building Effective Agents" research:

- **Keep it simple** — start with the simplest solution that works. Add complexity only when measured need exists.
- **Transparency over autonomy** — show the reasoning chain. Agents should explain what they do and why.
- **Well-documented tool interfaces** — describe tools precisely so the agent knows when and how to use each one.
- **Structured workflows over free-form** — use prompt chaining, routing tables, and sequential steps rather than open-ended instructions.
- **Augmented LLM pattern** — combine retrieval (codebase search, MCP tools), context (domain knowledge), and tools (terminal, file editing) into a cohesive workflow.
- **Orchestrator-worker** — for complex tasks, break into subtasks with clear inputs/outputs per step.
- **Evaluator-optimizer** — when quality matters, build in a review/verify step at the end of the workflow.

## Agent File Format

### Frontmatter (YAML)

```yaml
---
name: 'Agent Name'
description: One-sentence description of expertise, capabilities, and domain knowledge.
---
```

**Rules:**
- `name` — short, human-readable (e.g., `MongoDB Expert`, `Debug Expert`)
- `description` — concise but comprehensive; this is the **trigger mechanism** that determines when the agent is invoked. Include what the agent does AND what it knows.
- No other fields in frontmatter (no `tools:`, no `license:`)

### Body Structure

Follow this skeleton. Omit sections that don't apply, but preserve the order:

```markdown
{One-line mission statement in imperative voice}

When invoked:
- {4-6 bullet points describing key behaviors}

# Prerequisites                    ← optional, for MCP/tool-dependent agents

- {Tool/connection requirements}
- {Fallback behavior if tools unavailable}

# {Main Workflow}                  ← the core sequential process

## Step 1: {Verb phrase}
## Step 2: {Verb phrase}
## Step 3: {Verb phrase}
...

# {Domain Knowledge}               ← environment-specific conventions, patterns

## {Sub-section}
## {Sub-section}

# {General Best Practices}         ← universal domain knowledge

# Anti-Patterns                    ← table format

| Anti-Pattern | Why It's Wrong | Fix |
|---|---|---|
| ... | ... | ... |

# Important Rules                 ← final section, always last

- {Bullet list of hard constraints}
```

## Writing Style Rules

- **Imperative voice** throughout — "Analyze the query", not "You should analyze the query"
- **No "You are a..."** preamble in the mission statement — write it as a direct command
- **Tables** for structured data (categories, patterns, configurations, anti-patterns)
- **Code blocks** for examples, commands, and configuration snippets
- **Bullet lists** for rules, constraints, and checklists
- **No passive voice** — "Check the index" not "The index should be checked"
- **Concise** — every line must justify its token cost. Challenge: "Does the agent really need this?"

## Structural Patterns

### Mission Statement (Line 1 after frontmatter)

One sentence describing what the agent does. Imperative, active voice.

Good:
```
Analyze, optimize, and troubleshoot MongoDB usage across .NET services.
```

Bad:
```
You are a MongoDB performance optimization specialist who helps users...
```

### "When invoked" Block

4-6 bullets describing the agent's key behaviors. Start each with a verb.

```markdown
When invoked:
- Diagnose performance problems by correlating queries with cluster metrics
- Review schema design, index coverage, and aggregation pipelines
- Use MCP tools in readonly mode to inspect live cluster state
- Provide concrete before/after comparisons backed by data
```

### Prerequisites Section

Only for agents that depend on external tools (MCP servers, extensions). Include fallback behavior.

```markdown
# Prerequisites

- MongoDB MCP Server connected to the target cluster in **readonly mode**
- Atlas credentials on an M10+ cluster recommended for Performance Advisor access

Verify MCP connectivity first. If tools unavailable, report the gap and focus on codebase-only analysis.
```

### Workflow Steps

Sequential numbered steps with clear verbs. Use "Follow these steps in order" as the introductory line.

Each step should:
- Have a clear verb-phrase heading (`## Step 1: Gather Evidence`)
- List specific actions (numbered or bulleted)
- Reference concrete tools or commands where applicable
- State what to produce before moving to the next step

### Domain Knowledge Sections

Use tables for structured reference data. Include code examples where patterns are non-obvious.

**Convention tables:**
```markdown
| Collection | Type | Purpose |
|---|---|---|
| `{Entity}_snapshots` | `Snapshot` | Current entity state |
```

**Configuration tables:**
```markdown
| Class | Key Properties |
|---|---|
| `SqlChangeTrackerConfiguration` | `StoredProcedure`, `CronSchedule`, ... |
```

### Anti-Patterns Table

Always use the 3-column format: Anti-Pattern | Why It's Wrong | Fix

Target 8-12 entries. Each entry should be concrete and actionable.

### Important Rules Section

Final section. 5-8 hard constraints as bullet points. Include:
- Operating mode constraints (readonly, no modifications)
- Quality requirements (data-backed recommendations)
- Scope boundaries (what the agent should NOT do)

## Sizing Guidelines

| Agent Type | Target Lines | Example |
|---|---|---|
| Focused expert (single domain) | 150-200 | CSharpExpert |
| Domain + environment specialist | 250-350 | MongoDBExpert, MSSQLExpert |
| Multi-step diagnostic | 200-250 | DebugExpert |

Exceeding 400 lines signals the agent should be split or content moved to a skill.

## Creation Process

1. **Clarify scope** — determine what the agent does and does NOT do
2. **Fetch best practices** — retrieve `https://anthropic.com/research/building-effective-agents`
3. **Research the domain** — search the codebase, ADO repos, and wikis for environment-specific patterns
4. **Draft the agent** — follow the body structure skeleton above
5. **Review** — verify imperative style, no passive voice, no redundancy, appropriate line count
6. **Optimize** — remove anything the LLM already knows; keep only non-obvious, project-specific knowledge

## Common Mistakes to Avoid

- **Too generic** — an agent that just says "you are an expert in X" adds no value. Include specific workflows, tables, code patterns.
- **Too long** — context window is shared. If it exceeds 400 lines, extract domain knowledge into a skill.
- **Missing workflow** — agents without a structured step-by-step process produce inconsistent results.
- **Duplicating LLM knowledge** — don't teach the agent general programming. Focus on project-specific conventions and environment details.
- **Missing anti-patterns** — agents that only say what TO do are less effective than agents that also say what NOT to do.
- **No scope boundary** — always define what the agent should NOT handle (e.g., "DBA territory", "not server administration").
- **Passive voice** — undermines the imperative style and wastes tokens.
- **`tools:` in frontmatter** — VS Code agent format does not support tool declarations in frontmatter. Remove if present.
