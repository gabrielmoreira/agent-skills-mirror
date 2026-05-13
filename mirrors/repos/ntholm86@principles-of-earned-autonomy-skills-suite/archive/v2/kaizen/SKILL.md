---
name: kaizen
version: 2.11.0
description: 'Incremental improvement - diagnose, challenge blind spots, prioritize by impact, implement, verify. The core improvement cycle. Includes diagnostic vocabulary for unevenness, overburden, and waste. USE WHEN: audit, review, rate, improve, make impressive, quality loop, iterate, kaizen, evolve this, what would make this better, ROI analysis, blind spots, what am I missing.'
argument-hint: 'Specify the target to improve and optionally a focus area or quality concern'
---

# Kaizen

*Make it better. Prove it is better.*

Kaizen is the core improvement skill. Given a target, it finds what needs improving, determines the highest-leverage changes, implements them, and verifies the results. It is incremental - the target's fundamental structure is assumed to be sound.

**Part of the suite:** For orchestration, see **Kata**. For structural redesign, see **Kaikaku**. For reflection on the loop itself, see **Hansei**. For novelty probes that test reasoning quality, see **Shiken**.

## The Work

### Diagnose

Examine the target. What is its current state? What are its strengths? What are its weaknesses?

Three diagnostic lenses are available. They are vocabulary for thinking about different classes of problems, not a sequential procedure:

**Unevenness** - Where is the target inconsistent with itself? Mixed conventions, uneven quality distribution, asymmetric error handling, naming that follows three different patterns. Unevenness matters because it signals places where the target grew by accretion rather than design. It is often a root cause: fix the inconsistency and several downstream symptoms resolve.

**Overburden** - Where is the target asked to do too much? A module with too many responsibilities. A function that handles unrelated concerns. An interface that serves too many consumers. Overburden matters because it concentrates risk: the overburdened component is the one most likely to break, hardest to change, and most expensive to maintain.

**Waste** - Where does the target carry things that do not earn their existence? Dead code, unused abstractions, validation that can never fire, documentation that restates what the code already says. Waste matters because it creates cognitive load without contributing value. Every unnecessary element is something a future developer must understand before they can change what is around it.

Use these lenses as thinking tools. If the target's problems do not fit any of them, describe what you actually see. The diagnosis must reflect the target, not the categories. Context often warrants additional lenses beyond the three canonical ones — derive them from what you find (for example: P1 compliance, trail integrity, counter validity for a skill suite; security posture, test coverage for a web app). Whatever lenses you apply, name them.

For each finding: identify the root cause, not just the symptom. "This function is too long" is a symptom. "This function handles three unrelated responsibilities because they were added incrementally without refactoring" is a root cause.

**Show the diagnosis before moving on.** For each lens applied, state: the lens name, what was examined under it, and what was found (or "nothing actionable"). An observer should be able to read this output and know exactly which lenses were active and what each one revealed. Do not defer this to the GENBA entry — narrate it now.

**Silence is a valid outcome.** If genuine examination reveals nothing actionable, report that. "I examined the target with these lenses and found nothing that warrants change" is a legitimate diagnosis — it advances the convergence chain (Principle 3). Do not manufacture findings to justify the run.

### Challenge Blind Spots

After the initial diagnosis, ask: *What am I not seeing?*

- Are there structural assumptions I have not questioned?
- Does the target have patterns that look intentional but might be accidental?
- Am I anchored to the most obvious finding and missing a subtler, more important one?
- Would someone from a different tradition (different language, different domain, different era of software engineering) see something I missed?

This is not performative skepticism. It is a genuine attempt to catch what the first pass missed. If you find nothing, say so. Do not manufacture blind spots to appear thorough.

**Show the blind-spot examination before moving on.** State each question you asked. Answer it — in one sentence if the answer is short, in more if the answer matters. "I asked X; it revealed nothing" is more trustworthy than silence. If a question surfaces a real gap, that gap becomes a finding and enters the prioritization phase.

### Prioritize

Rank findings by impact. The question is not "how many things can I fix" but "what single change would improve this target the most?"

For each finding, consider:
- How much does this hurt the target's ability to serve its purpose?
- How much risk does this create?
- How hard is it to fix?
- Does fixing this resolve other findings too?

Start with the highest-leverage change. Not everything needs to be fixed in one pass. Kaizen is incremental.

**Show the ranking before implementing.** List the findings in order with a one-sentence rationale for each rank position. An observer should not need to read the implementation to understand why you acted on what you acted on.

### Implement

Make the changes. For each change:
- State what you are changing and why before making the change
- Make the change
- Verify the change is correct (tests pass, no regressions, the improvement is real)

Show the reasoning, not just the diff. "I consolidated these three naming conventions into one because the inconsistency was the root cause of the confusing API surface" - not just a diff.

### Verify

After all changes:
- Does the target still work? Run tests, check types, verify builds.
- Are the improvements real? Compare the current state to the prior state on the specific findings you addressed.
- Did any changes introduce new problems?

### Self-Evaluate

Score the target against the measurements derived during Grasp (Kata Step 1). These are the measurements that were determined to matter for *this specific target* — not a universal checklist.

Be honest. A score that inflates progress undermines the loop. If the target was 4/10 before and your changes brought it to 5/10, say 5/10 — not 7/10 because you tried hard.

If a formal scoring rubric exists for this target (e.g., Rubric v3 for the skill suite), score against it. If the measurements were context-derived, score against those and state the scores explicitly so the next evaluator can compare on the same basis — or revise the measurements if they no longer fit.

The scores go into the GENBA entry. The gap between current scores and the Target Condition is what drives the next run.

If the diagnosis found nothing actionable and no changes were made, score the target at its current level (+0.0 delta). This is not failure — it is evidence of convergence. Record the silence explicitly: what was examined, why nothing warranted change, and that the run advances the P3 silence chain.

## Evidence

An observer reading the kiroku session after this skill completes should be able to find:

- **What was examined and found.** Which aspects of the target were looked at. Each finding with its root cause identified (not just the symptom). If nothing warranted change, an explicit statement of that with reasoning — silence is a valid outcome that advances Principle 3.
- **What was selected.** The highest-leverage finding chosen and why alternatives were ranked lower.
- **What was changed and verified.** For each change: the before-state, the after-state, and evidence that the change is correct (tests pass, no regressions). For silence: confirmation that no regression was introduced.
- **The score.** End-of-run score against the measurements from Kata Step 1, with delta from the prior run.

Mark decisions `[!DECISION]`, realizations `[!REALIZATION]`, reversals `[!REVERSAL]` in the session as they occur.
