---
name: brainstorming
description: "Structured idea generation and diverge/converge facilitation. Use when the user says 'let's brainstorm', 'I need ideas', or 'help me explore options'."
---

# Brainstorming Facilitation

## Goal

Generate a wide range of ideas on a topic, then converge on the most promising ones through structured evaluation — not gut feeling.

---

## Activation

1. Ask: "What topic or problem are we brainstorming?"
2. Ask: "What kind of output do you want? Options:"
   - A: Feature ideas
   - B: Technical approaches / solutions
   - C: Business models / monetization strategies
   - D: Problem definitions / root causes
   - E: Custom
3. Ask: "How many ideas do you want to explore? (suggested: 10–20)"

---

## Phase 1: Diverge — Generate Without Judgment

Generate {n} ideas. Use multiple frames:
- **Conventional** (the obvious approach)
- **Analogy** (how does another industry solve this?)
- **Inversion** (what if we did the opposite?)
- **Constraint removal** (what if time/money/tech weren't a limit?)
- **User extreme** (what would the most demanding user want?)
- **Simplification** (what's the 10% version?)

Present ideas in a numbered list with a 1-line description each.

⏸️ **STOP** — let the user react before evaluation. Ask: "Any immediate reactions? Anything to add?"

---

## Phase 2: Cluster

Group related ideas together. Present clusters with names.

Ask: "Does this grouping look right? Any ideas to move?"

⏸️ **STOP** — wait for feedback.

---

## Phase 3: Converge — Score by Criteria

For each cluster/idea, score across:
| Criterion | Weight |
|-----------|--------|
| Impact (if it works, how much does it matter?) | 40% |
| Feasibility (how realistic to implement?) | 30% |
| Novelty (how differentiated from obvious approaches?) | 20% |
| Risk (how much could go wrong?) | 10% (inverse) |

Score 1–5 per criterion. Show weighted total.

---

## Phase 4: Top Picks

Present top 3 ideas with brief rationale.

Ask:
> "Which of these should we develop further? Or would you like to explore a different angle?"

Options:
1. Turn top pick into a product brief (`product-brief`)
2. Explore the idea further with more brainstorming rounds
3. Save this output and return to your agent
4. Done

⏸️ **STOP** — wait for choice.

---

## Output (Optional Save)

If the user wants to save the output, write to `{planning_artifacts}/briefs/brainstorm-{topic-slug}-{date}.md`.
