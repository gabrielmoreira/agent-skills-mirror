---
name: review-adversarial
description: "Challenge a design, plan, or artifact by actively looking for weaknesses, risks, and blind spots. Use when the user says 'challenge this design', 'red team this', 'steelman the alternative', or 'find what we missed'."
---

# Adversarial Review Workflow

## Goal

Act as a rigorous challenger — not a critic for its own sake, but a structured devil's advocate. Find the real risks, unspoken assumptions, and failure modes that optimistic reviews miss.

---

## Step 1: Load the Artifact

Ask: What are we reviewing?
- PRD / product brief
- Architecture design / ADR
- Epic or story set
- Migration plan
- Any other document or decision

Read the artifact in full before proceeding.

---

## Step 2: Assumption Mapping

List every explicit and implicit assumption the artifact makes:

| # | Assumption | Evidence for it | What if it's wrong? |
|---|-----------|-----------------|---------------------|
| 1 | ...       | ...             | ...                 |

Flag any assumption with no evidence as **HIGH RISK**.

---

## Step 3: Failure Mode Analysis

For each major decision or component, ask:

- **What is the most likely way this fails?** (not the most dramatic — the most probable)
- **What external dependency could break this?**
- **What happens under 10x the expected load / scale / users?**
- **What does an adversary (competitor, attacker, regulator) do to break this?**

Produce a table:

| Component / Decision | Failure Mode | Probability (H/M/L) | Impact (H/M/L) | Mitigation |
|---------------------|-------------|---------------------|----------------|------------|
| ...                 | ...         | ...                 | ...            | ...        |

---

## Step 4: Steelman the Strongest Alternative

Identify the best alternative approach that was NOT chosen.

Argue for it as strongly as possible:
- Why it would work better
- What evidence or assumptions favour it
- What the current choice loses by not going this way

This is not a recommendation to switch — it surfaces the real trade-off.

---

## Step 5: Blind Spot Scan

Ask the questions no one wants to ask:
- What is this design completely silent on? (security, cost, ops burden, rollback)
- Who has a stake in this failing? (internal politics, competing teams, vendors)
- What regulatory or compliance angle was ignored?
- What would a new team member find confusing in 6 months?

---

## Step 6: Output

Produce an adversarial review report:

```
## Adversarial Review — {artifact title}

### Critical Assumptions (unsupported)
- ...

### Top 3 Failure Modes
1. [component] — [failure] — [mitigation]
2. ...
3. ...

### Strongest Alternative (steelmanned)
...

### Blind Spots
- ...

### Recommended Actions Before Proceeding
1. ...
2. ...
```

Save to `{docsPath}/analysis/adversarial-review-{slug}.md`.
