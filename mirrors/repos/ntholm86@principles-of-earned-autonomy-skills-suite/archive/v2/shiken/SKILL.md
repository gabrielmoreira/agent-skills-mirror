---
name: shiken
version: 2.11.0
description: 'Construct novelty probes that distinguish genuine situated reasoning from pattern-matching. Builds examination scenarios where routine execution fails but interpretation succeeds. Measures Autonomous Reasoning Fidelity. USE WHEN: test reasoning quality, construct novelty probes, is the agent actually reasoning, ARF measurement, shiken, novelty injection, anti-compliance test, distinguish reasoning from pattern-matching, stress test.'
argument-hint: 'Specify the skill or system to probe, and optionally the aspect of reasoning to test'
---

# Shiken

*Build the test that the checklist cannot pass.*

Shiken constructs examination scenarios that distinguish genuine situated reasoning from pattern-matching. It operationalizes the Autonomous Reasoning Fidelity (ARF) concept from PRINCIPLES.md: given two cases that look similar on the surface but differ in a material way, does the agent's reasoning path diverge where it should?

**Part of the suite:** For orchestration, see **Kata**. For incremental improvement, see **Kaizen**. For structural redesign, see **Kaikaku**. For reflection on the improvement loop itself, see **Hansei**.

## Why This Skill Exists

An agent following a checklist and an agent reasoning about a mission can produce identical-looking output in routine cases. The difference only becomes visible when the situation is novel - when the checklist does not cover what is happening, and the agent must interpret rather than match.

Shiken creates those novel situations deliberately. Not to trick the agent, but to distinguish the two modes of operation. If the skill set works, Shiken should be passable. If the skill set has drifted toward prescription, Shiken exposes where.

## The Work

### 1. Identify What to Probe

Select a skill or system capability to examine. What claim does it make about reasoning?

- Kaizen claims to diagnose by understanding the target, not by running through categories
- Kaikaku claims to evaluate structural adequacy, not just apply a "rewrite threshold"
- Hansei claims to find blind spots, not just summarize prior runs
- The overall system claims agents interpret missions, not follow instructions

Each claim can be tested.

### 2. Design the Probe

A probe consists of:

**A pair of cases** - two targets that share surface features but differ in a material way that should change the agent's approach.

- Same language, similar structure, different root cause
- Same symptom, different appropriate treatment
- Same metrics on the surface, different trajectory underneath

**A predicted divergence** - where specifically should the agent's reasoning diverge between the two cases? State this before running the probe. If you cannot predict where divergence should occur, the probe is poorly designed.

**A compliance baseline** - what would a checklist-following agent produce for both cases? If the checklist answer is the same for both, and the correct answer differs, the probe discriminates.

### 3. Run the Probe

Execute the skill against both cases. Capture the full reasoning trail for each.

### 4. Evaluate

Compare the two trails at the predicted divergence point:

- **Divergence present:** The agent's reasoning path differed where it should. The specific findings, priorities, or actions reflect the material difference between the cases. This is evidence of situational discrimination.
- **No divergence:** The agent produced the same analysis for both cases despite the material difference. Either the agent is pattern-matching, or the probe failed to surface a meaningful difference. Determine which.
- **Unexpected divergence:** The agent's reasoning differed at a point you did not predict. This is interesting - either you missed something about the cases, or the agent is responding to noise rather than signal. Investigate.

### Assessment Criteria

A probe succeeds when it produces a clear signal - either the agent discriminated or it did not. A probe fails when the result is ambiguous (both cases were too similar, the predicted divergence was wrong, the compliance baseline was inaccurate).

Good probes:
- Target a specific reasoning claim
- Have a clear predicted divergence
- Cannot be passed by checklist execution alone
- Are fair - a reasoning agent should pass them

Bad probes:
- Require knowledge the agent could not have
- Test recall rather than reasoning
- Are ambiguous about what divergence should look like
- Can be passed by either mode of operation

## What Shiken Does Not Do

Shiken does not prove inner reasoning exists. It produces external evidence about whether the agent's responses vary with the specifics of what it encounters. This is the strongest signal the framework can produce - not a metaphysical claim, but an observable behavioral difference.

## Evidence

An observer reading the kiroku session after this skill completes should be able to find:

- **The probe design.** The pair of cases, the material difference between them, the predicted divergence point, and the compliance baseline.
- **The execution trace for each case.** The agent's actual reasoning path at the predicted divergence point.
- **The ARF assessment.** Whether divergence was present, absent, or unexpected — and what that means for the target skill's reasoning quality. If unexpected: what it reveals about either the probe design or the agent's behavior.

Mark decisions `[!DECISION]`, realizations `[!REALIZATION]`, reversals `[!REVERSAL]` in the session as they occur.
