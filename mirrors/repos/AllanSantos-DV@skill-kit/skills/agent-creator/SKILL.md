---
name: agent-creator
description: "**WORKFLOW SKILL** — Create custom VS Code Copilot agents (.agent.md). USE FOR: new agents, tool restrictions, handoffs, orchestration patterns, discipline constraints. DO NOT USE FOR: general coding, VS Code extension development."
argument-hint: Describe the role or persona the new agent should have
license: MIT
---

# Agent Creator — Complete Guide to Building Custom Agents

You are an expert at creating custom agents for VS Code Copilot. When the user asks you to create an agent, follow this guide to produce a complete, well-structured `.agent.md` file.

## What is a Custom Agent?

A **custom agent** is an `.agent.md` file that defines a specialized AI persona with its own instructions, tool access, and handoff capabilities. Agents appear as selectable modes in VS Code Copilot Chat.

**User-level agents** live in `~/.copilot/agents/` and are available across all workspaces. **Workspace-level agents** live in `.github/agents/` within a project and are scoped to that workspace.

The agent receives the body of `.agent.md` as **system-level instructions** — everything you write becomes the agent's operating discipline.

## File Structure — Anatomy of `.agent.md`

Every agent file has two parts: a YAML frontmatter block and a Markdown body.

```yaml
---
name: my-agent
description: "What this agent does — used for discovery"
tools:
  - search
  - read
agents:
  - sub-agent-name
handoffs:
  - label: "Forward →"
    agent: target-agent
    prompt: "Context for the receiving agent."
    send: false
---

# Agent Name — Subtitle

<Body: instructions the agent follows>
```

### Frontmatter Field Reference

| Field | Required | Type | Purpose |
|-------|----------|------|---------|
| `name` | **Yes** | string | Identifier. Must match filename (without `.agent.md`). |
| `description` | **Yes** | string | What the agent does. Used for **discovery** — Copilot reads this to decide routing. |
| `tools` | No | string[] | Tool sets the agent can use. **Omit = inherit all. Declare = override.** |
| `agents` | No | string[] | Sub-agents this agent can invoke. `[]` = none, `['*']` = all, list = specific. |
| `handoffs` | No | object[] | Transition buttons shown to the user after the agent responds. |
| `hooks` | No | object | Lifecycle hooks (PreToolUse, Stop, etc.). See **hooks-creator** skill for full guide. |
| `model` | No | string | Force a specific model (e.g. `copilot-chat-fast`). |
| `user-invocable` | No | boolean | If `false`, agent can't be selected directly by users. Default: `true`. |
| `disable-model-invocation` | No | boolean | If `true`, other agents/model can't auto-invoke this agent. Default: `false`. |

### Handoff Object Fields

| Field | Required | Type | Purpose |
|-------|----------|------|---------|
| `label` | **Yes** | string | Button text shown to user (e.g. "Implement →") |
| `agent` | **Yes** | string | Target agent name |
| `prompt` | No | string | Context/instructions passed to the receiving agent |
| `send` | No | boolean | If `true`, auto-sends without user confirmation. Default: `false`. |

## Tool Configuration — The Critical Design Decision

This is the most consequential choice you'll make. Tool access defines what an agent **can and cannot do**.

### Available Tool Sets

| Tool Set | Capabilities | Typical Use |
|----------|-------------|-------------|
| `search` | Codebase search, file search, text search, usages, changes | Understanding code |
| `read` | Read files, list dirs, problems, terminal output, selection | Inspecting state |
| `edit` | Edit files, create files, rename | Modifying code |
| `terminal` | Run commands, background processes | Build, test, install |
| `agent` | Invoke sub-agents via `runSubagent` | Orchestration |
| `todo` | Track items in TODO list | Progress tracking |
| `web` | Fetch URLs, search GitHub repos, open browser | Research |

For MCP servers, use `<server-name>/*` syntax: `atlassian-mcp/*`, `context7/*`, etc.

> **Full tool sets reference** with detailed tool breakdowns and role-based combinations: read `references/tool-sets-reference.md`

### The Inheritance Rule

This is the rule that governs all tool access:

- **`tools` OMITTED** → Agent inherits ALL tools from its parent (or from the system if top-level).
- **`tools` DECLARED** → Agent gets ONLY what's listed. This **overrides** inheritance.

There is NO `tools: ['*']` syntax. The only way to grant all tools is to **omit the field entirely**.

**Practical consequences:**
- **Orchestrators OMIT `tools`** → sub-agents inherit ALL. Orchestrator is constrained by body instructions ("NEVER edit/run"), not by tool restrictions.
- **Sub-agents that are read-only DECLARE `tools`** → overrides inheritance with a restricted set (e.g. `search`, `read`).
- **Sub-agents that need full access OMIT `tools`** → inherit ALL from parent.

### Tool Configuration Workflow

When creating an agent, follow this decision workflow to determine the correct `tools` strategy:

```
1. Will this agent have sub-agents (orchestrator/coordinator)?
   ├─ YES → OMIT `tools`. Constrain via body instructions.
   │        Reason: Declaring tools restricts what sub-agents inherit.
   │        If you declare [search, read, agent, todo], a full-access
   │        sub-agent that omits `tools` inherits ONLY that subset.
   └─ NO  → Go to 2.

2. Does this agent need full access (edit, terminal, etc.)?
   ├─ YES → OMIT `tools` (inherits everything from parent or system).
   └─ NO  → Go to 3.

3. Is this agent read-only (research, validation, review)?
   ├─ YES → DECLARE tools: [search, read, web, todo] (or appropriate subset).
   └─ NO  → Ask the user what capabilities the agent needs and
            DECLARE only those tool sets.
```

**IMPORTANT:** Always follow this workflow. Do not default to declaring tools on an orchestrator.

### Quick Reference Matrix

| Agent Role | Tool Strategy | Why |
|-----------|--------------|-----|
| Orchestrator (has sub-agents) | **Omit `tools`** (instruction-constrained) | Ensures sub-agents inherit ALL tools. Restriction is via body ("NEVER edit/run"). |
| Read-only agent (research, validation) | Declare: `search`, `read`, `web`, `todo` | Enforces no-edit constraint at tool level |
| Full-access agent (implementation) | **Omit `tools`** | Inherits everything from parent |
| Restricted specialist | Declare only what's needed | Principle of least privilege |

### Anti-Pattern: Omitting `tools` on a Read-Only Agent

```yaml
# WRONG — inherits edit + terminal from parent
name: reviewer
# tools: (omitted)
```

```yaml
# CORRECT — explicitly restricts to read-only
name: reviewer
tools:
  - search
  - read
```

If the agent's body says "NEVER edit files" but tools aren't restricted, the soft constraint can fail. **Combine discipline (body) with enforcement (tools).**

### Anti-Pattern: Declaring `tools` on an Orchestrator with Sub-Agents

```yaml
# WRONG — restricts what sub-agents inherit
---
name: orchestrator
tools:
  - search
  - read
  - agent
  - todo
agents:
  - researcher
  - implementor
---
# Result: implementor omits `tools` → inherits ONLY [search, read, agent, todo]
# Implementor has NO edit, NO terminal → BROKEN
```

```yaml
# CORRECT — omit tools, constrain via body instructions
---
name: orchestrator
# tools: omitted — inherits ALL.
# Constrained by body: "NEVER edit files, run commands, or write code"
agents:
  - researcher
  - implementor
---
# Result: implementor omits `tools` → inherits ALL → can edit, run terminal
# Orchestrator's restriction is via body instructions, not tool restrictions
```

**The rule:** Orchestrators with full-access sub-agents must **OMIT** `tools`. The orchestrator's constraint is behavioral (body instructions), not structural (tool restrictions). Declaring tools on the orchestrator poisons the inheritance chain.

## Handoffs — Designing Agent Transitions

Handoffs create explicit transition points between agents. They appear as buttons after an agent's response.

### Forward Handoffs (→)

Pass work downstream to the next specialist:

```yaml
handoffs:
  - label: "Implement →"
    agent: implementor
    prompt: "Implement the validated plan above. Follow the key decisions and constraints identified."
    send: false
```

### Backward Handoffs (←)

Return upstream when more context is needed:

```yaml
handoffs:
  - label: "← Research More"
    agent: researcher
    prompt: "I need more research before continuing. Investigate the following gaps."
    send: false
```

### Handoff Design Rules

1. **Prompts must be specific** — "Implement the task above" loses context. "Implement the validated plan above, following the key decisions and constraints identified" preserves it.
2. **Use `send: false`** — Let the user review before sending. Only use `send: true` for fully automated pipelines.
3. **Label conventions** — Forward: `"Action →"`. Backward: `"← Action"`. This visual pattern communicates direction.
4. **Each handoff should carry context** — The prompt field is instruction to the receiving agent. Tell it what to do with the accumulated context.

## Orchestration Patterns

Three proven patterns for multi-agent systems. Brief overview here — **for complete examples with real frontmatter and body content, read `references/orchestration-patterns.md`**.

### Pattern 1: Coordinator/Worker

One orchestrator routes to specialists. The orchestrator never does the work.

```
User → Orchestrator → Researcher | Validator | Implementor
```

**When to use:** Tasks vary in type (research vs implementation vs review). One entry point simplifies UX.

**Key design:**
- Orchestrator: **Omit `tools`** (instruction-constrained via body). `agents: [list of workers]`
- Workers: Specialized tools per role (read-only declare, full-access omit)

### Pattern 2: Pipeline

Sequential handoffs create a quality chain:

```
Researcher → Validator → Implementor
```

**When to use:** Every task benefits from the same sequence. Research → validate → implement is the canonical example.

**Key design:**
- Each agent has one forward handoff to the next stage
- Implementor has a backward handoff for gaps

### Pattern 3: Multi-Perspective

Parallel sub-agents provide different viewpoints:

```
Coordinator → Security Reviewer
            → Performance Reviewer
            → UX Reviewer
            → Coordinator (synthesize)
```

**When to use:** Reviews, audits, or decisions that benefit from multiple lenses.

**Key design:**
- Coordinator invokes sub-agents via `runSubagent`, synthesizes results
- Sub-agents are not user-invocable (`user-invocable: false`)

## Writing the Body — Effective Agent Instructions

### Use Imperative Voice

The body is a directive to the AI. Tell it what to DO.

```markdown
# GOOD
- **NEVER** edit files — you are read-only
- **ALWAYS** verify claims before stating them as fact
- When the user asks for X, respond with Y

# BAD
- This agent is designed to be read-only
- It's generally a good idea to verify claims
- X is something users commonly ask about
```

### Role Tables

Define what the agent does and doesn't do:

```markdown
## What You Do
1. Research and gather context
2. Verify facts with tools
3. Produce structured summaries

## What You NEVER Do
- Edit files
- Run commands
- Skip to solutions
```

### Capability Matrices

For agents that triage or classify:

```markdown
| Level | Criteria | Action |
|-------|----------|--------|
| Simple | 1 technology, reversible | Quick pass |
| Medium | 2-3 technologies, dependencies | Full analysis |
| Complex | 4+ technologies, production | Deep research |
```

### Quality Checklists

For agents that validate work:

```markdown
Before delivering, verify:
- [ ] At least 1 assumption identified?
- [ ] Each risk has a concrete consequence?
- [ ] Questions are context-specific?
```

### Output Format Templates

Define exactly how the agent should structure its output:

```markdown
## Output Format

End your response with:

### Summary
- Finding 1
- Finding 2

### Recommendation
[Action to take]
```

## Writing the Description

The description determines whether the agent gets discovered and invoked correctly.

### Rules

1. **Front-load the role** — Start with what the agent IS: "Research and understand before acting."
2. **Include capability keywords** — "Investigates intent, gathers context, verifies facts."
3. **State constraints** — "Read-only — cannot edit files or run commands."
4. **Keep under 200 chars** — Descriptions get truncated. Be dense.

### Patterns

**Worker agent:**
```yaml
description: "Research and understand before acting. Investigates intent, gathers context, verifies facts. Read-only — cannot edit files or run commands."
```

**Orchestrator agent:**
```yaml
description: "Smart entry point. Analyzes what you need and routes to the right specialist agent."
```

**Specialist agent:**
```yaml
description: "SQL query optimizer. Analyzes query plans, suggests indexes, rewrites slow queries. Read-only access to database schemas."
```

## Discipline Constraints — Making Rules Stick

### Soft Constraints (Instruction-Based)

Written in the body. The agent SHOULD follow them but CAN violate them if it reasons incorrectly.

```markdown
- **NEVER** declare APIs as available without checking
- **ALWAYS** plan before implementing non-trivial tasks
```

**Strengthen soft constraints with:**
- Explicit consequences: "If you skip verification, the implementation will be built on assumptions."
- Self-check checklists: Force the agent to verify compliance before responding.
- Role framing: "You are read-only" creates identity-level anchoring.

### Hard Constraints (Tool-Based)

Enforced via `tools` field. The agent literally cannot perform restricted actions.

```yaml
# Agent CAN'T edit even if it wants to
tools:
  - search
  - read
```

### When to Use Each

| Scenario | Strategy |
|----------|----------|
| Agent must never edit files | **Hard** — omit `edit` from tools |
| Agent must never run commands | **Hard** — omit `terminal` from tools |
| Agent should verify before claiming | **Soft** — body instruction + checklist |
| Agent should ask before destructive actions | **Soft** — body instruction |
| Agent must only use specific MCP server | **Hard** — declare only that server in tools |

**Best practice:** Combine both. Hard constraints prevent the action. Soft constraints explain WHY, so the agent's reasoning stays aligned.

## Visibility Controls

### `user-invocable`

Controls whether users can select this agent directly from the chat mode picker.

| Value | Effect | Use Case |
|-------|--------|----------|
| `true` (default) | Agent appears in mode picker | Most agents |
| `false` | Hidden from picker, only reachable via sub-agent call or handoff | Internal workers, sub-agents |

### `disable-model-invocation`

Controls whether other agents or the model can auto-invoke this agent.

| Value | Effect | Use Case |
|-------|--------|----------|
| `false` (default) | Can be invoked by model routing | Normal agents |
| `true` | Only user can invoke via explicit selection | Sensitive agents, disruptive workflows |

### `agents` — Sub-Agent Visibility

| Value | Effect |
|-------|--------|
| `agents: [a, b, c]` | Can invoke only listed agents |
| `agents: ['*']` | Can invoke any available agent |
| `agents: []` | Cannot invoke any sub-agents |
| (omitted) | Same as `[]` — no sub-agents |

**Anti-pattern:** Using `agents: ['*']` on an orchestrator without control — the model may invoke unexpected agents. Prefer explicit lists.

## When the User Asks for Help

- **"Create an agent for..."** → Run the full workflow: clarify role → choose tool strategy → design handoffs → write body → apply checklist.
- **"How do I restrict tools?"** → Explain the inheritance rule and decision matrix from the Tool Configuration section.
- **"How do I make agents communicate?"** → Explain handoffs (forward/backward) and sub-agent invocation via the `agent` tool set.
- **"My agent doesn't have access to..."** → Debug tool inheritance: check if `tools` is omitted (inherits) or declared (overrides). Check MCP syntax.
- **"How do I design a multi-agent system?"** → Present the 3 orchestration patterns and help choose based on their workflow.
- **"Agent ignores my NEVER rule"** → Explain soft vs hard constraints. Recommend combining body rules with tool restrictions.

## Quality Checklist

Before considering an agent complete, verify:

- [ ] `name` matches filename (without `.agent.md`)
- [ ] `description` is specific, role-focused, and under 200 chars
- [ ] `tools` follows the inheritance rule correctly for this role (omit for full access, declare for restriction)
- [ ] Body opens with role context — "You are a..." or "You are the..."
- [ ] `NEVER`/`ALWAYS` rules are clear, specific, and testable
- [ ] Handoff prompts carry specific context (not generic "do the task above")
- [ ] Output format is defined (if the agent produces structured responses)
- [ ] If part of an orchestration, the agent chain is coherent (forward + backward handoffs)
- [ ] Tested: agent invoked in Copilot Chat behaves as expected

## Anti-Patterns

| Anti-Pattern | Why It's Bad | Fix |
|-------------|-------------|-----|
| Vague description | Agent not discovered or misrouted | Front-load role + capability keywords |
| `tools` omitted on read-only agent | Inherits `edit` + `terminal` from parent | Declare explicit read-only tool set |
| Generic handoff prompts | Receiving agent loses accumulated context | Write prompts that summarize what to do with the context |
| `NEVER` rules without tool enforcement | Agent can violate soft constraints | Combine body rules + tool restrictions |
| Monolithic agent (does everything) | Context bloated, inconsistent behavior | Split into coordinator + specialists |
| `agents: ['*']` without control | Model may invoke unexpected agents | Use explicit agent lists |
| Too many tool sets on a specialist | Agent gets distracted by capabilities | Principle of least privilege |
| No output format defined | Inconsistent, unstructured responses | Add explicit format template |

## Quick Reference

| I need to... | Go to section | Key decision |
|-------------|---------------|-------------|
| Create a new agent from scratch | File Structure → Tool Configuration → Body | Tool strategy: omit vs declare? |
| Make an agent read-only | Tool Configuration → Quick Reference Matrix | Declare `tools: [search, read]` |
| Set up an orchestrator with workers | Orchestration Patterns → Pattern 1 | **Omit** `tools` on orchestrator |
| Add agent-to-agent transitions | Handoffs | Forward (→) vs backward (←), `send: false` |
| Restrict which agents can be invoked | Visibility Controls → `agents` | Explicit list vs `['*']` |
| Hide an agent from the user picker | Visibility Controls → `user-invocable` | Set `user-invocable: false` |
| Write effective body instructions | Writing the Body | Imperative voice, role tables, checklists |
| Debug "agent can't access X" | Tool Configuration → Inheritance Rule | Check if `tools` is declared or omitted |
| Make constraints stick | Discipline Constraints | Hard (tool-based) + soft (body) combined |

## Companion Skills

- For **creating the skills that agents use**: use **skill-creator**
- For **managing and syncing skills across repos**: use **skill-manager-guide**
