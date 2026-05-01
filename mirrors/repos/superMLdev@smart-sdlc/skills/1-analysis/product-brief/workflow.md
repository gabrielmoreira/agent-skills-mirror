# Product Brief — Workflow

**Goal:** Define what is being built, who it serves, and why it matters. The product brief is the pre-PRD artifact that aligns the team on purpose before diving into requirements.

**Output:** `{planning_artifacts}/briefs/{project_name}-brief.md`

---

## Activation

Read `{project-root}/_superml/config.yml`. Greet the user and say:
> "Let's build your product brief. I'll ask you a series of questions — answer what you know, say 'skip' for anything you're not sure about yet, and I'll flag it as an open question."

Then begin with Section 1.

---

## Section 1: Problem Statement

Ask the user:
1. **What problem are you solving?** Describe the pain point in one sentence.
2. **Who has this problem?** Be specific — job role, industry, context.
3. **How are they solving it today?** Current workarounds, alternatives, competitors.
4. **Why is today's solution inadequate?** What gap exists?
5. **What does success look like for the user?** What changes in their day?

Synthesize answers into a Problem Statement block. Present it back and ask for confirmation.

⏸️ **STOP** — wait for approval before proceeding.

---

## Section 2: Solution Hypothesis

Ask:
1. **What is the core idea?** One sentence.
2. **What unique value does it deliver?** What can users do that they couldn't before?
3. **What is explicitly out of scope?** What won't this solve?
4. **What assumptions are we making?** List the top 3 riskiest assumptions.

---

## Section 3: Target Audience

Ask:
1. **Primary user persona** — role, context, goals
2. **Secondary users or stakeholders** — anyone else affected
3. **Scale** — how many users? Individual, team, enterprise?
4. **Technical profile** — how technical are the users?

---

## Section 4: Success Metrics

Ask:
1. **How will we know if this worked?** Primary success metric (KPI)
2. **Secondary metrics** — engagement, retention, accuracy, speed
3. **Anti-goals** — what does failure look like?

---

## Section 5: Constraints & Context

Ask:
1. **Timeline** — any hard deadline or milestone?
2. **Technology constraints** — existing stack to integrate with?
3. **Regulatory or compliance requirements?**
4. **Budget or team size constraints?**
5. **Greenfield or brownfield?** If brownfield, point to `document-project` output.

---

## Output: Write the Product Brief

Compile all sections into `{planning_artifacts}/briefs/{project_name}-brief.md`:

```markdown
---
project: {project_name}
created: {date}
status: draft
version: 1
---

# {project_name} — Product Brief

## Problem Statement
...

## Solution Hypothesis
...

## Target Audience
...

## Success Metrics
...

## Constraints & Context
...

## Open Questions
[List any skipped items or unresolved assumptions]
```

Present the document. Ask: "Does this capture it accurately? Any changes before we proceed?"

⏸️ **STOP** — wait for approval.

---

## Completion

> "✅ Product brief saved to `{planning_artifacts}/briefs/{project_name}-brief.md`.
>
> **Suggested next step:** Talk to Leo (Product Manager) to convert this brief into a full PRD with detailed requirements."
