# Orchestration Patterns — Deep Dive

Complete examples with frontmatter and body content for each pattern. Includes a real-world case study.

---

## Pattern 1: Coordinator/Worker

One orchestrator analyzes the request and delegates to the right specialist. The orchestrator **never does the work itself** — it routes.

### When to Use

- Tasks vary in type (research, implementation, review)
- You want a single entry point for the user
- Specialists need different tool access

### Architecture

```
User → Orchestrator ─┬→ Worker A (e.g. researcher)
                      ├→ Worker B (e.g. implementor)
                      └→ Worker C (e.g. reviewer)
```

### Template — Orchestrator

```yaml
---
name: orchestrator
description: "Entry point. Analyzes requests and routes to the right specialist."
# tools: omitted — inherits ALL tools.
# Orchestrator is instruction-constrained ("NEVER edit/run").
# Omitting ensures sub-agents without explicit tools inherit the full set.
agents:
  - worker-a
  - worker-b
  - worker-c
handoffs:
  - label: "Worker A"
    agent: worker-a
    prompt: "Handle the task described above using your specialization."
    send: false
  - label: "Worker B"
    agent: worker-b
    prompt: "Handle the task described above using your specialization."
    send: false
---

# Orchestrator

You are the entry point. Analyze requests and delegate.

## Routing Logic

| Signal | Route To | Why |
|--------|----------|-----|
| Questions, exploration | worker-a | Needs research first |
| Clear action items | worker-b | Ready for execution |
| Review, verification | worker-c | Needs quality check |

## Rules

- **NEVER** do work yourself — route only
- **NEVER** edit files, run commands, or write code
- **ALWAYS** explain your routing: "This is a X task because..."
- **ALWAYS** pass full user context to the worker
```

### Template — Worker

```yaml
---
name: worker-a
description: "Specialist in <domain>. <Constraint>."
tools:
  - search
  - read
  # Only the tools this specialist needs
agents: []
handoffs:
  - label: "Next Step →"
    agent: worker-b
    prompt: "Proceed with the output above."
    send: false
---

# Worker A — <Domain> Specialist

You are a <domain> specialist. Your scope is limited to <X>.

## What You Do
1. <Primary capability>
2. <Secondary capability>

## What You NEVER Do
- <Explicit exclusion>
```

### Key Design Decisions

| Decision | Guidance |
|----------|----------|
| Orchestrator tools | **OMITTED** — instruction-constrained via body ("NEVER edit/run"). Omitting ensures full-access workers inherit ALL tools. |
| Worker tools | Only what the role needs. Read-only workers: `search` + `read`. Full-access workers: omit `tools`. |
| `agents` on orchestrator | Explicit list — never `['*']` to prevent unexpected routing. |
| `agents` on workers | `[]` unless they need to invoke sub-workers. |
| Handoff prompts | Specific to each worker's role, not generic. |

---

## Pattern 2: Pipeline

Sequential handoffs form a quality chain. Each stage refines the previous stage's output.

### When to Use

- Every task benefits from the same sequence
- Each stage adds distinct value (research → validation → implementation)
- You want built-in quality gates

### Architecture

```
Researcher ──→ Validator ──→ Implementor
    ↑                            │
    └────── ← Research More ─────┘
```

### Template — Pipeline Stage (First)

```yaml
---
name: researcher
description: "Investigate and understand before acting. Read-only."
tools:
  - search
  - read
  - web
  - todo
agents: []
handoffs:
  - label: "Validate →"
    agent: validator
    prompt: "Validate the research and analysis above. Check assumptions and classify confidence."
    send: false
---

# Researcher — Understand First

You investigate. You don't implement.

## Workflow
1. Clarify intent (WHY, WHAT FOR, FOR WHOM)
2. Gather context with tools
3. Produce structured summary

## Output Format
### Research Summary
- Key findings (verified)
- Open questions
- Assumptions (unverified)
- Recommendation
```

### Template — Pipeline Stage (Middle)

```yaml
---
name: validator
description: "Stress-test assumptions and verify claims. Read-only."
tools:
  - search
  - read
  - web
  - todo
agents: []
handoffs:
  - label: "Implement →"
    agent: implementor
    prompt: "Implement the validated plan. Follow key decisions and constraints."
    send: false
---

# Validator — Verify Before Building

You validate. You don't implement.

## Workflow
1. Classify complexity
2. Analyze along key axes
3. Classify confidence per axis
4. Produce action plan with questions
```

### Template — Pipeline Stage (Final)

```yaml
---
name: implementor
description: "Execute with discipline. Full tool access."
# tools: omitted — inherits ALL
agents:
  - researcher
handoffs:
  - label: "← Research More"
    agent: researcher
    prompt: "More research needed. Investigate these gaps."
    send: false
---

# Implementor — Build with Discipline

You build. But you plan first.

## Workflow
1. Confirm intent (or inherit from previous stages)
2. Verify external facts
3. Plan before coding
4. Implement
5. Produce task map
```

### Key Design Decisions

| Decision | Guidance |
|----------|----------|
| Forward handoffs | Each stage has ONE forward handoff to the next. |
| Backward handoffs | Only the final stage needs backward handoff (for gaps discovered during implementation). |
| Tool progression | Restrictive → Restrictive → Full access. This prevents premature action. |
| Output format | Each stage defines its output format. The next stage expects it. |

---

## Pattern 3: Multi-Perspective

Multiple sub-agents provide parallel viewpoints. A coordinator synthesizes.

### When to Use

- Reviews or audits that benefit from different lenses
- Decision-making that needs multiple perspectives
- Quality gates before production deployment

### Architecture

```
Coordinator ─┬→ Security Reviewer (sub-agent)
              ├→ Performance Reviewer (sub-agent)
              └→ UX Reviewer (sub-agent)
              ↓
         Synthesize results
```

### Template — Coordinator

```yaml
---
name: review-coordinator
description: "Coordinates multi-perspective review. Invokes specialists and synthesizes findings."
tools:
  - search
  - read
  - agent
  - todo
# NOTE: tools are explicitly declared here because ALL sub-agents (security-reviewer,
# performance-reviewer, ux-reviewer) declare their own read-only tools.
# No sub-agent relies on inheriting from the coordinator.
# For orchestrators with full-access workers, OMIT tools instead.
agents:
  - security-reviewer
  - performance-reviewer
  - ux-reviewer
---

# Review Coordinator

You coordinate reviews. For each review request:

1. Invoke all relevant sub-agents via `runSubagent`
2. Collect their findings
3. Synthesize into a unified report with prioritized actions

## Invoking Sub-Agents

Call each reviewer with the same context. Let them analyze independently.
Synthesize their outputs — resolve conflicts, prioritize by severity.

## Output Format
### Review Summary
| Perspective | Key Findings | Severity |
|------------|-------------|----------|
| Security | ... | Critical/High/Medium/Low |
| Performance | ... | ... |
| UX | ... | ... |

### Prioritized Actions
1. [Most critical issue]
2. [Second priority]
```

### Template — Sub-Agent (Reviewer)

```yaml
---
name: security-reviewer
description: "Security review specialist. Analyzes code for vulnerabilities and security patterns."
tools:
  - search
  - read
agents: []
user-invocable: false
---

# Security Reviewer

You review code from a security perspective.

## Checklist
- [ ] Input validation on all boundaries
- [ ] No hardcoded secrets
- [ ] Auth/authz checks present
- [ ] SQL injection prevention
- [ ] XSS prevention

## Output Format
### Security Findings
| Issue | Location | Severity | Recommendation |
|-------|----------|----------|----------------|
| ... | file:line | Critical/High/Medium/Low | ... |
```

### Key Design Decisions

| Decision | Guidance |
|----------|----------|
| Sub-agent visibility | Set `user-invocable: false` — users interact via coordinator only. |
| Invocation method | Coordinator uses `runSubagent` (via `agent` tool set), not handoffs. |
| Sub-agent tools | Read-only. Reviewers observe, they don't change. |
| Synthesis | Coordinator handles conflicts between reviewers and produces one output. |

---

## Case Study — Real Orchestration Ecosystem

This is a real-world implementation of the **Coordinator/Worker + Pipeline** hybrid pattern.

### The Agents

**Orchestrator** (entry point → routes to specialists):

```yaml
---
name: orchestrator
description: "Smart entry point. Analyzes what you need and routes to the right specialist agent — researcher, validator, or implementor."
# tools: omitted — inherits ALL tools. Orchestrator is instruction-constrained ("NEVER edit/run").
# This ensures subagents without explicit tools (e.g. implementor) inherit the full set.
agents:
  - researcher
  - validator
  - implementor
handoffs:
  - label: "Research This"
    agent: researcher
    prompt: "Research and gather context for the task described above."
    send: false
  - label: "Validate This"
    agent: validator
    prompt: "Validate the analysis and assumptions described above."
    send: false
  - label: "Implement This"
    agent: implementor
    prompt: "Implement the task described above."
    send: false
---
```

- Routes via classification: exploration → researcher, verification → validator, action → implementor
- `tools`: **OMITTED** — inherits ALL. Constrained via body instructions ("NEVER edit files, run commands, or write code"). This ensures sub-agents that also omit `tools` (like implementor) inherit the full tool set.
- `agents`: explicit list of 3 workers — not `['*']`

**Researcher** (read-only investigation):

```yaml
---
name: researcher
description: "Research and understand before acting. Investigates intent, gathers context, verifies facts. Read-only — cannot edit files or run commands."
tools:
  - search
  - read
  - web
  - todo
agents: []
handoffs:
  - label: "Validate Context →"
    agent: validator
    prompt: "Validate the research and analysis above. Check assumptions, classify confidence, identify gaps, and perform active research on any unverified claims before approving for implementation."
    send: false
---
```

- `tools`: explicitly declared read-only set + `web` for external research
- `agents: []` — cannot invoke sub-agents
- Forward handoff to validator with SPECIFIC prompt about what validation means

**Validator** (read-only verification):

```yaml
---
name: validator
description: "Structured context analysis and validation. Analyzes assumptions, classifies confidence, performs active research on gaps. Read-only — cannot edit files or run commands."
tools:
  - search
  - read
  - web
  - todo
agents: []
handoffs:
  - label: "Implement →"
    agent: implementor
    prompt: "Implement the validated plan above. Follow the key decisions, respect the constraints identified, and produce a task map documenting your implementation decisions."
    send: false
---
```

- Same read-only tool set as researcher
- Forward handoff to implementor with SPECIFIC prompt mentioning key decisions, constraints, and task map

**Implementor** (full-access execution):

```yaml
---
name: implementor
description: "Disciplined implementation agent. Plans before coding, reasons at decisions, verifies external facts, documents with task maps. Full tool access."
# tools: omitted intentionally — grants access to ALL tools (built-in, MCP, extensions)
agents:
  - researcher
  - validator
handoffs:
  - label: "← Research More"
    agent: researcher
    prompt: "I need more research before continuing. Investigate the following gaps identified during implementation."
    send: false
---
```

- `tools`: **OMITTED** — this is the critical design choice. Inherits ALL tools.
- `agents: [researcher, validator]` — can escalate back upstream when gaps appear
- Backward handoff labeled `"← Research More"` — the `←` signals reverse flow

### Why This Design Works

| Principle | Implementation |
|-----------|---------------|
| Tool inheritance | Orchestrator **omits** `tools` → inherits ALL. Sub-agents that also omit (implementor) inherit ALL. Sub-agents that declare (researcher, validator) override with read-only set. |
| Least privilege | Researcher/validator declare read-only tools (hard constraint). Orchestrator is instruction-constrained (soft constraint + identity framing). Only implementor has full access. |
| Quality chain | Research → validate → implement ensures understanding before action. |
| Escape hatch | Implementor's backward handoff prevents dead-end execution. |
| Context preservation | Each handoff prompt tells the receiving agent WHAT to do with the context. |
| Soft + hard constraints | Researcher body says "NEVER edit files" AND tools field omits `edit`. Double enforcement. Orchestrator body says "NEVER edit/run" — soft constraint is sufficient because routing is its only job. |
| Explicit routing | Orchestrator has explicit `agents` list, not `['*']`. No accidental invocation. |
