---
name: kaikaku
version: 2.11.0
description: 'Radical redesign evaluation. When incremental improvement has converged too low or the architecture is fundamentally wrong, Kaikaku determines whether to redesign and produces a migration plan if warranted. USE WHEN: redesign, start over, rethink, rewrite, architecture is wrong, kaizen isnt working, converged too low, fundamental change, kaikaku, radical change, clean slate, rearchitect, pivot.'
argument-hint: 'Specify the target to evaluate for radical redesign and optionally the evidence that incremental improvement is insufficient'
---

# Kaikaku

*Is the structure capable of reaching the goal, or must it be replaced?*

Kaikaku evaluates whether a target needs radical redesign rather than incremental improvement. This is a consequential decision - replacing structure is expensive, risky, and often unnecessary. Kaikaku's job is to make that judgment honestly.

**Part of the suite:** For orchestration, see **Kata**. For incremental improvement, see **Kaizen**. For reflection on the loop itself, see **Hansei**. For novelty probes that test reasoning quality, see **Shiken**.

## When Kaikaku Applies

Kaikaku is appropriate when there is evidence that incremental improvement cannot reach the target's goals:

- Kaizen runs have converged at a score well below the target
- The same class of finding keeps recurring across multiple runs because it is structural
- The target's architecture creates constraints that no amount of local improvement can resolve
- The cost of maintaining the current structure exceeds the cost of replacing it

Kaikaku is NOT appropriate simply because the target is imperfect, because someone wants to rewrite, or because new technology exists. Desire for novelty is not evidence of structural inadequacy.

## The Evaluation

### Establish the Evidence

What specifically suggests that incremental improvement is insufficient? This must be concrete:

- Show the Kaizen trajectory. Where did it converge? Why can it not go higher?
- Identify the structural constraints. What about the current design prevents reaching the goal?
- Distinguish structural problems from implementation problems. A bad function can be rewritten. A bad architecture constrains every function.

### Assess the Current Ceiling

Given the current structure, what is the best possible state achievable through incremental improvement? This is the ceiling question:

- If every individual component were as good as it could be within this structure, would the result meet the goals?
- If yes, the problem is execution, not architecture. Kaizen is sufficient. Stop here.
- If no, identify the specific structural constraint that creates the ceiling.

### Evaluate the Redesign Cost

If the ceiling is too low, what would replacement require?

- What is the scope of the redesign? Full replacement or partial restructuring?
- What is preserved? What knowledge, data, or interfaces survive the transition?
- What is the migration path? How does the system move from current to new without breaking?
- What is the risk? What could go wrong? What is the rollback plan?

### Make the Recommendation

One of three outcomes:

1. **Continue with Kaizen.** The structure can reach the goal. The evidence for redesign was insufficient or the findings were implementation problems, not structural ones. State why specifically.

2. **Partial restructuring.** Some structural changes are needed, but full replacement is unnecessary. Identify the specific components that need restructuring and why, preserving everything else.

3. **Full redesign.** The current structure cannot reach the goal. Produce a migration plan: what the new structure looks like, what it preserves from the current state, how to migrate, and what the rollback plan is if the redesign fails.

### The Honesty Requirement

Kaikaku must resist two biases:

- **The sunk-cost bias:** "We have invested too much to throw it away." If the structure cannot reach the goal, investment in the wrong structure is not a reason to continue.
- **The novelty bias:** "This would be more elegant if we rewrote it." Elegance is not a reason for redesign. The question is whether the goals are reachable, not whether the code is pretty.

State which bias you checked yourself against and what you found.

## Evidence

An observer reading the kiroku session after this skill completes should be able to find:

- **The evidence marshaled.** What specifically argued for or against radical redesign: the Kaizen trajectory shown, the structural constraint identified (or why none exists), the distinction between structural and implementation problems.
- **The ceiling assessment.** The estimated best-achievable state under the current structure and whether that meets the goals.
- **The recommendation.** Which of the three outcomes was reached (continue Kaizen, partial restructuring, or full redesign), with full rationale. If redesign: the migration plan.
- **The bias checks.** An explicit assessment of sunk-cost bias and novelty bias — not just that they were checked, but what was found.

Mark decisions `[!DECISION]`, realizations `[!REALIZATION]`, reversals `[!REVERSAL]` in the session as they occur.
