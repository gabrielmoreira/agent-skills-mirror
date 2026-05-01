---
id: instruction_clarity
name: Instruction Clarity
---

# Instruction Clarity

Evaluates whether the plugin's prompts (SKILL.md, agent .md files, command .md files)
are clear, specific, and unambiguous enough that an LLM will follow them consistently.

## What to look for

- **Structured phases or steps** — Does the plugin break work into defined stages?
- **Explicit scope** — Is it clear what the plugin does and does NOT do?
- **Output format specification** — Does it tell the LLM exactly how to format responses?
- **Unambiguous language** — Are instructions precise, or could an LLM interpret them multiple ways?
- **Role definition** — For agents, is the persona/mindset clearly established?

## Scoring rubric

| Score | Criteria |
|-------|----------|
| **5** | Numbered workflow phases or clearly structured steps (sub-steps not required for simple plugins). Explicit scope boundaries. Defined output format with example. MUST/MUST NOT rules. |
| **4** | Clear role definition. Specific do/don't rules. Structured sections. Output format mentioned but not demonstrated. |
| **3** | Instructions tell the agent its goal, but lack phases, scope boundaries, or output format. Agent can complete the task but results vary between runs. |
| **2** | Instructions are <10 lines or use vague language ("do a good job", "be helpful"). Agent will guess at behavior. |
| **1** | No SKILL.md / agent .md, or only a title with no instructions. |

## What a 5 looks like

- SKILL.md with numbered workflow phases
- Explicit "you MUST" / "you MUST NOT" rules
- Defined output format with example
- Scope boundaries ("only review files in the PR, not the entire repo")

## Scoring examples

### Score 5 — deep-review

```markdown
## Workflow
Phase 1: GATHER CONTEXT (you, the orchestrator)
    ├── Collect change information
    ├── Fetch file contents
    └── Write to /tmp/deep-review-context.yaml

Phase 2: PARALLEL ANALYSIS (three agents)
    ├── Verify context file exists
    ├── Spawn three agents in parallel
    └── Each reads context file independently

Phase 3: SYNTHESIS (you, the orchestrator)
    ├── Reconcile into final review
    └── Delete context file (always)
```

Why it scores 5: Numbered workflow phases, explicit role definitions per agent,
defined output format, clear scope boundaries.

### Score 2 — hello-skills

```markdown
Greet the user warmly and ask how you can help them today.
If the user provided their name, use it in the greeting.
Keep the greeting friendly and encouraging and enclose the message in ASCII art.
```

Why it scores 2: Three lines of vague instructions, no phases, no output format,
no scope boundaries. The LLM will guess at behavior.
